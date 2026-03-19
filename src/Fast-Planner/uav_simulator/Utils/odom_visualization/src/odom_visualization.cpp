#include <iostream>
#include <string.h>
#include <rclcpp/rclcpp.hpp>
#include <tf2_ros/transform_broadcaster.h>
#include <geometry_msgs/msg/transform_stamped.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <geometry_msgs/msg/pose_with_covariance_stamped.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <geometry_msgs/msg/point.hpp>
#include <nav_msgs/msg/path.hpp>
#include <sensor_msgs/msg/range.hpp>
#include <visualization_msgs/msg/marker.hpp>
#include <std_msgs/msg/color_rgba.hpp>
#include "armadillo"
#include "pose_utils.h"

using namespace arma;
using namespace std;

static string mesh_resource;
static double color_r, color_g, color_b, color_a, cov_scale;
bool cross_config = false;
bool tf45 = false;
bool cov_pos = false;
bool cov_vel = false;
bool cov_color = false;
bool origin = false;
bool isOriginSet = false;
colvec poseOrigin(6);
rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr posePub;
rclcpp::Publisher<nav_msgs::msg::Path>::SharedPtr pathPub;
rclcpp::Publisher<visualization_msgs::msg::Marker>::SharedPtr velPub;
rclcpp::Publisher<visualization_msgs::msg::Marker>::SharedPtr covPub;
rclcpp::Publisher<visualization_msgs::msg::Marker>::SharedPtr covVelPub;
rclcpp::Publisher<visualization_msgs::msg::Marker>::SharedPtr trajPub;
rclcpp::Publisher<visualization_msgs::msg::Marker>::SharedPtr sensorPub;
rclcpp::Publisher<visualization_msgs::msg::Marker>::SharedPtr meshPub;
rclcpp::Publisher<sensor_msgs::msg::Range>::SharedPtr heightPub;
std::shared_ptr<tf2_ros::TransformBroadcaster> broadcaster;
geometry_msgs::msg::PoseStamped poseROS;
nav_msgs::msg::Path pathROS;
visualization_msgs::msg::Marker velROS;
visualization_msgs::msg::Marker covROS;
visualization_msgs::msg::Marker covVelROS;
visualization_msgs::msg::Marker trajROS;
visualization_msgs::msg::Marker sensorROS;
visualization_msgs::msg::Marker meshROS;
sensor_msgs::msg::Range heightROS;
rclcpp::Node::SharedPtr node_;

void odom_callback(const nav_msgs::msg::Odometry::SharedPtr msg) {
    if (msg->header.frame_id == string("null"))
        return;
    colvec pose(6);
    pose(0) = msg->pose.pose.position.x;
    pose(1) = msg->pose.pose.position.y;
    pose(2) = msg->pose.pose.position.z;
    colvec q(4);
    q(0) = msg->pose.pose.orientation.w;
    q(1) = msg->pose.pose.orientation.x;
    q(2) = msg->pose.pose.orientation.y;
    q(3) = msg->pose.pose.orientation.z;
    pose.rows(3, 5) = R_to_ypr(quaternion_to_R(q));
    colvec vel(3);
    vel(0) = msg->twist.twist.linear.x;
    vel(1) = msg->twist.twist.linear.y;
    vel(2) = msg->twist.twist.linear.z;

    if (origin && !isOriginSet) {
        isOriginSet = true;
        poseOrigin = pose;
    }
    if (origin) {
        vel = trans(ypr_to_R(pose.rows(3, 5))) * vel;
        pose = pose_update(pose_inverse(poseOrigin), pose);
        vel = ypr_to_R(pose.rows(3, 5)) * vel;
    }

    // Pose
    poseROS.header = msg->header;
    poseROS.header.stamp = msg->header.stamp;
    poseROS.header.frame_id = string("world");
    poseROS.pose.position.x = pose(0);
    poseROS.pose.position.y = pose(1);
    poseROS.pose.position.z = pose(2);
    q = R_to_quaternion(ypr_to_R(pose.rows(3, 5)));
    poseROS.pose.orientation.w = q(0);
    poseROS.pose.orientation.x = q(1);
    poseROS.pose.orientation.y = q(2);
    poseROS.pose.orientation.z = q(3);
    posePub->publish(poseROS);

    // Velocity
    colvec yprVel(3);
    yprVel(0) = atan2(vel(1), vel(0));
    yprVel(1) = -atan2(vel(2), norm(vel.rows(0, 1), 2));
    yprVel(2) = 0;
    q = R_to_quaternion(ypr_to_R(yprVel));
    velROS.header.frame_id = string("world");
    velROS.header.stamp = msg->header.stamp;
    velROS.ns = string("velocity");
    velROS.id = 0;
    velROS.type = visualization_msgs::msg::Marker::ARROW;
    velROS.action = visualization_msgs::msg::Marker::ADD;
    velROS.pose.position.x = pose(0);
    velROS.pose.position.y = pose(1);
    velROS.pose.position.z = pose(2);
    velROS.pose.orientation.w = q(0);
    velROS.pose.orientation.x = q(1);
    velROS.pose.orientation.y = q(2);
    velROS.pose.orientation.z = q(3);
    velROS.scale.x = norm(vel, 2);
    velROS.scale.y = 0.05;
    velROS.scale.z = 0.05;
    velROS.color.a = 1.0;
    velROS.color.r = color_r;
    velROS.color.g = color_g;
    velROS.color.b = color_b;
    velPub->publish(velROS);

    // Path
    static rclcpp::Time prevt(msg->header.stamp);
    rclcpp::Time current_t(msg->header.stamp);
    if ((current_t - prevt).seconds() > 0.1) {
        prevt = current_t;
        pathROS.header = poseROS.header;
        pathROS.poses.push_back(poseROS);
        pathPub->publish(pathROS);
    }

    // Covariance color
    double r = 1;
    double g = 1;
    double b = 1;
    bool G = msg->twist.covariance[33];
    bool V = msg->twist.covariance[34];
    bool L = msg->twist.covariance[35];
    if (cov_color) {
        r = G;
        g = V;
        b = L;
    }

    // Covariance Position
    if (cov_pos) {
        mat P(6, 6);
        for (int j = 0; j < 6; j++)
            for (int i = 0; i < 6; i++)
                P(i, j) = msg->pose.covariance[i + j * 6];
        colvec eigVal;
        mat eigVec;
        eig_sym(eigVal, eigVec, P.submat(0, 0, 2, 2));
        if (det(eigVec) < 0) {
            for (int k = 0; k < 3; k++) {
                mat eigVecRev = eigVec;
                eigVecRev.col(k) *= -1;
                if (det(eigVecRev) > 0) {
                    eigVec = eigVecRev;
                    break;
                }
            }
        }
        covROS.header.frame_id = string("world");
        covROS.header.stamp = msg->header.stamp;
        covROS.ns = string("covariance");
        covROS.id = 0;
        covROS.type = visualization_msgs::msg::Marker::SPHERE;
        covROS.action = visualization_msgs::msg::Marker::ADD;
        covROS.pose.position.x = pose(0);
        covROS.pose.position.y = pose(1);
        covROS.pose.position.z = pose(2);
        q = R_to_quaternion(eigVec);
        covROS.pose.orientation.w = q(0);
        covROS.pose.orientation.x = q(1);
        covROS.pose.orientation.y = q(2);
        covROS.pose.orientation.z = q(3);
        covROS.scale.x = sqrt(eigVal(0)) * cov_scale;
        covROS.scale.y = sqrt(eigVal(1)) * cov_scale;
        covROS.scale.z = sqrt(eigVal(2)) * cov_scale;
        covROS.color.a = 0.4;
        covROS.color.r = r * 0.5;
        covROS.color.g = g * 0.5;
        covROS.color.b = b * 0.5;
        covPub->publish(covROS);
    }

    // Covariance Velocity
    if (cov_vel) {
        mat P(3, 3);
        for (int j = 0; j < 3; j++)
            for (int i = 0; i < 3; i++)
                P(i, j) = msg->twist.covariance[i + j * 6];
        mat R = ypr_to_R(pose.rows(3, 5));
        P = R * P * trans(R);
        colvec eigVal;
        mat eigVec;
        eig_sym(eigVal, eigVec, P);
        if (det(eigVec) < 0) {
            for (int k = 0; k < 3; k++) {
                mat eigVecRev = eigVec;
                eigVecRev.col(k) *= -1;
                if (det(eigVecRev) > 0) {
                    eigVec = eigVecRev;
                    break;
                }
            }
        }
        covVelROS.header.frame_id = string("world");
        covVelROS.header.stamp = msg->header.stamp;
        covVelROS.ns = string("covariance_velocity");
        covVelROS.id = 0;
        covVelROS.type = visualization_msgs::msg::Marker::SPHERE;
        covVelROS.action = visualization_msgs::msg::Marker::ADD;
        covVelROS.pose.position.x = pose(0);
        covVelROS.pose.position.y = pose(1);
        covVelROS.pose.position.z = pose(2);
        q = R_to_quaternion(eigVec);
        covVelROS.pose.orientation.w = q(0);
        covVelROS.pose.orientation.x = q(1);
        covVelROS.pose.orientation.y = q(2);
        covVelROS.pose.orientation.z = q(3);
        covVelROS.scale.x = sqrt(eigVal(0)) * cov_scale;
        covVelROS.scale.y = sqrt(eigVal(1)) * cov_scale;
        covVelROS.scale.z = sqrt(eigVal(2)) * cov_scale;
        covVelROS.color.a = 0.4;
        covVelROS.color.r = r;
        covVelROS.color.g = g;
        covVelROS.color.b = b;
        covVelPub->publish(covVelROS);
    }

    // Color Coded Trajectory
    static colvec ppose = pose;
    static rclcpp::Time pt(msg->header.stamp);
    rclcpp::Time t(msg->header.stamp);
    if ((t - pt).seconds() > 0.5) {
        trajROS.header.frame_id = string("world");
        trajROS.header.stamp = node_->now();
        trajROS.ns = string("trajectory");
        trajROS.type = visualization_msgs::msg::Marker::LINE_LIST;
        trajROS.action = visualization_msgs::msg::Marker::ADD;
        trajROS.pose.position.x = 0;
        trajROS.pose.position.y = 0;
        trajROS.pose.position.z = 0;
        trajROS.pose.orientation.w = 1;
        trajROS.pose.orientation.x = 0;
        trajROS.pose.orientation.y = 0;
        trajROS.pose.orientation.z = 0;
        trajROS.scale.x = 0.1;
        trajROS.scale.y = 0;
        trajROS.scale.z = 0;
        trajROS.color.r = 0.0;
        trajROS.color.g = 1.0;
        trajROS.color.b = 0.0;
        trajROS.color.a = 0.8;
        geometry_msgs::msg::Point p;
        p.x = ppose(0);
        p.y = ppose(1);
        p.z = ppose(2);
        trajROS.points.push_back(p);
        p.x = pose(0);
        p.y = pose(1);
        p.z = pose(2);
        trajROS.points.push_back(p);
        std_msgs::msg::ColorRGBA color;
        color.r = r;
        color.g = g;
        color.b = b;
        color.a = 1;
        trajROS.colors.push_back(color);
        trajROS.colors.push_back(color);
        ppose = pose;
        pt = t;
        trajPub->publish(trajROS);
    }

    // Sensor availability
    sensorROS.header.frame_id = string("world");
    sensorROS.header.stamp = msg->header.stamp;
    sensorROS.ns = string("sensor");
    sensorROS.type = visualization_msgs::msg::Marker::TEXT_VIEW_FACING;
    sensorROS.action = visualization_msgs::msg::Marker::ADD;
    sensorROS.pose.position.x = pose(0);
    sensorROS.pose.position.y = pose(1);
    sensorROS.pose.position.z = pose(2) + 1.0;
    sensorROS.pose.orientation.w = q(0);
    sensorROS.pose.orientation.x = q(1);
    sensorROS.pose.orientation.y = q(2);
    sensorROS.pose.orientation.z = q(3);
    string strG = G ? string(" GPS ") : string("");
    string strV = V ? string(" Vision ") : string("");
    string strL = L ? string(" Laser ") : string("");
    sensorROS.text = "| " + strG + strV + strL + " |";
    sensorROS.color.a = 1.0;
    sensorROS.color.r = 1.0;
    sensorROS.color.g = 1.0;
    sensorROS.color.b = 1.0;
    sensorROS.scale.z = 0.5;
    sensorPub->publish(sensorROS);

    // Laser height measurement
    double H = msg->twist.covariance[32];
    heightROS.header.frame_id = string("height");
    heightROS.header.stamp = msg->header.stamp;
    heightROS.radiation_type = sensor_msgs::msg::Range::ULTRASOUND;
    heightROS.field_of_view = 5.0 * M_PI / 180.0;
    heightROS.min_range = -100;
    heightROS.max_range = 100;
    heightROS.range = H;
    heightPub->publish(heightROS);

    // Mesh model - 如果mesh_resource为空或加载失败，使用立方体
    meshROS.header.frame_id = string("world");
    meshROS.header.stamp = msg->header.stamp;
    meshROS.ns = "mesh";
    meshROS.id = 0;
    meshROS.action = visualization_msgs::msg::Marker::ADD;
    meshROS.pose.position.x = msg->pose.pose.position.x;
    meshROS.pose.position.y = msg->pose.pose.position.y;
    meshROS.pose.position.z = msg->pose.pose.position.z;
    q(0) = msg->pose.pose.orientation.w;
    q(1) = msg->pose.pose.orientation.x;
    q(2) = msg->pose.pose.orientation.y;
    q(3) = msg->pose.pose.orientation.z;
    if (cross_config) {
        colvec ypr = R_to_ypr(quaternion_to_R(q));
        ypr(0) += 45.0 * M_PI / 180.0;
        q = R_to_quaternion(ypr_to_R(ypr));
    }
    meshROS.pose.orientation.w = q(0);
    meshROS.pose.orientation.x = q(1);
    meshROS.pose.orientation.y = q(2);
    meshROS.pose.orientation.z = q(3);
    meshROS.color.a = color_a;
    meshROS.color.r = color_r;
    meshROS.color.g = color_g;
    meshROS.color.b = color_b;
    
    // 如果没有指定mesh_resource，使用立方体
    if (mesh_resource.empty()) {
        meshROS.type = visualization_msgs::msg::Marker::CUBE;
        meshROS.scale.x = 0.6;
        meshROS.scale.y = 0.6;
        meshROS.scale.z = 0.2;
    } else {
        // 使用mesh - ROS2支持package://路径
        meshROS.type = visualization_msgs::msg::Marker::MESH_RESOURCE;
        meshROS.scale.x = 1.5;
        meshROS.scale.y = 1.5;
        meshROS.scale.z = 1.5;
        meshROS.mesh_resource = mesh_resource;
        meshROS.mesh_use_embedded_materials = false;
    }
    
    meshPub->publish(meshROS);

    // 始终发布 world->base_link tf，供RViz使用
    {
        geometry_msgs::msg::TransformStamped tf_base;
        tf_base.header.stamp = msg->header.stamp;
        tf_base.header.frame_id = "world";
        tf_base.child_frame_id = "base_link";
        tf_base.transform.translation.x = msg->pose.pose.position.x;
        tf_base.transform.translation.y = msg->pose.pose.position.y;
        tf_base.transform.translation.z = msg->pose.pose.position.z;
        tf_base.transform.rotation.w = msg->pose.pose.orientation.w;
        tf_base.transform.rotation.x = msg->pose.pose.orientation.x;
        tf_base.transform.rotation.y = msg->pose.pose.orientation.y;
        tf_base.transform.rotation.z = msg->pose.pose.orientation.z;
        broadcaster->sendTransform(tf_base);
    }

    // TF for raw sensor visualization
    if (tf45) {
        geometry_msgs::msg::TransformStamped transform;
        transform.header.stamp = msg->header.stamp;
        transform.header.frame_id = "world";
        transform.child_frame_id = "base";
        transform.transform.translation.x = pose(0);
        transform.transform.translation.y = pose(1);
        transform.transform.translation.z = pose(2);
        transform.transform.rotation.w = q(0);
        transform.transform.rotation.x = q(1);
        transform.transform.rotation.y = q(2);
        transform.transform.rotation.z = q(3);
        broadcaster->sendTransform(transform);
        geometry_msgs::msg::TransformStamped transform45;
        transform45.header.stamp = msg->header.stamp;
        transform45.header.frame_id = "base";
        transform45.child_frame_id = "laser";
        transform45.transform.translation.x = 0;
        transform45.transform.translation.y = 0;
        transform45.transform.translation.z = 0;
        colvec y45 = zeros<colvec>(3);
        y45(0) = 45.0 * M_PI / 180;
        colvec q45 = R_to_quaternion(ypr_to_R(y45));
        transform45.transform.rotation.w = q45(0);
        transform45.transform.rotation.x = q45(1);
        transform45.transform.rotation.y = q45(2);
        transform45.transform.rotation.z = q45(3);
        broadcaster->sendTransform(transform45);

        geometry_msgs::msg::TransformStamped transform45v;
        transform45v.header.stamp = msg->header.stamp;
        transform45v.header.frame_id = "base";
        transform45v.child_frame_id = "vision";
        transform45v.transform.translation.x = 0;
        transform45v.transform.translation.y = 0;
        transform45v.transform.translation.z = 0;
        transform45v.transform.rotation.w = q45(0);
        transform45v.transform.rotation.x = q45(1);
        transform45v.transform.rotation.y = q45(2);
        transform45v.transform.rotation.z = q45(3);
        broadcaster->sendTransform(transform45v);

        geometry_msgs::msg::TransformStamped transform90;
        transform90.header.stamp = msg->header.stamp;
        transform90.header.frame_id = "base";
        transform90.child_frame_id = "height";
        transform90.transform.translation.x = 0;
        transform90.transform.translation.y = 0;
        transform90.transform.translation.z = 0;
        colvec p90 = zeros<colvec>(3);
        p90(1) = 90.0 * M_PI / 180;
        colvec q90 = R_to_quaternion(ypr_to_R(p90));
        transform90.transform.rotation.w = q90(0);
        transform90.transform.rotation.x = q90(1);
        transform90.transform.rotation.y = q90(2);
        transform90.transform.rotation.z = q90(3);
        broadcaster->sendTransform(transform90);
    }
}

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    node_ = rclcpp::Node::make_shared("odom_visualization");

    node_->declare_parameter("mesh_resource", "package://odom_visualization/meshes/hummingbird.dae");
    node_->declare_parameter("color.r", 1.0);
    node_->declare_parameter("color.g", 0.0);
    node_->declare_parameter("color.b", 0.0);
    node_->declare_parameter("color.a", 1.0);
    node_->declare_parameter("origin", false);
    node_->declare_parameter("cross_config", false);
    node_->declare_parameter("tf45", false);
    node_->declare_parameter("covariance_scale", 100.0);
    node_->declare_parameter("covariance_position", false);
    node_->declare_parameter("covariance_velocity", false);
    node_->declare_parameter("covariance_color", false);

    mesh_resource = node_->get_parameter("mesh_resource").as_string();
    color_r = node_->get_parameter("color.r").as_double();
    color_g = node_->get_parameter("color.g").as_double();
    color_b = node_->get_parameter("color.b").as_double();
    color_a = node_->get_parameter("color.a").as_double();
    origin = node_->get_parameter("origin").as_bool();
    cross_config = node_->get_parameter("cross_config").as_bool();
    tf45 = node_->get_parameter("tf45").as_bool();
    cov_scale = node_->get_parameter("covariance_scale").as_double();
    cov_pos = node_->get_parameter("covariance_position").as_bool();
    cov_vel = node_->get_parameter("covariance_velocity").as_bool();
    cov_color = node_->get_parameter("covariance_color").as_bool();

    auto sub = node_->create_subscription<nav_msgs::msg::Odometry>("odom", 100, odom_callback);
    posePub = node_->create_publisher<geometry_msgs::msg::PoseStamped>("pose", 100);
    pathPub = node_->create_publisher<nav_msgs::msg::Path>("path", 100);
    velPub = node_->create_publisher<visualization_msgs::msg::Marker>("velocity", 100);
    covPub = node_->create_publisher<visualization_msgs::msg::Marker>("covariance", 100);
    covVelPub = node_->create_publisher<visualization_msgs::msg::Marker>("covariance_velocity", 100);
    trajPub = node_->create_publisher<visualization_msgs::msg::Marker>("trajectory", 100);
    sensorPub = node_->create_publisher<visualization_msgs::msg::Marker>("sensor", 100);
    meshPub = node_->create_publisher<visualization_msgs::msg::Marker>("/odom_visualization/robot", 100);
    heightPub = node_->create_publisher<sensor_msgs::msg::Range>("height", 100);
    broadcaster = std::make_shared<tf2_ros::TransformBroadcaster>(node_);

    rclcpp::spin(node_);
    rclcpp::shutdown();

    return 0;
}



