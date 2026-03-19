#include <iostream>
#include <rclcpp/rclcpp.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <geometry_msgs/msg/pose.hpp>
#include <geometry_msgs/msg/pose_array.hpp>
#include <geometry_msgs/msg/vector3.hpp>
#include <nav_msgs/msg/path.hpp>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2/LinearMath/Matrix3x3.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>
#include "sample_waypoints.h"
#include <vector>
#include <deque>
#include <boost/format.hpp>
#include <eigen3/Eigen/Dense>

using namespace std;
using bfmt = boost::format;

class WaypointGenerator : public rclcpp::Node {
public:
    WaypointGenerator() : Node("waypoint_generator") {
        this->declare_parameter("waypoint_type", "manual");
        waypoint_type_ = this->get_parameter("waypoint_type").as_string();
        
        is_odom_ready_ = false;
        trigged_time_ = rclcpp::Time(0);
        
        // Publishers - 使用 TRANSIENT_LOCAL 确保晚订阅的节点也能收到最后一条 waypoint
        auto waypoint_qos = rclcpp::QoS(rclcpp::KeepLast(10)).transient_local().reliable();
        pub_waypoints_ = this->create_publisher<geometry_msgs::msg::PoseStamped>("/waypoint_generator/waypoints", waypoint_qos);
        pub_waypoints_vis_ = this->create_publisher<geometry_msgs::msg::PoseArray>("waypoints_vis", 10);
        
        // Subscribers
        sub_odom_ = this->create_subscription<nav_msgs::msg::Odometry>(
            "odom", 10, std::bind(&WaypointGenerator::odom_callback, this, std::placeholders::_1));
        sub_goal_ = this->create_subscription<geometry_msgs::msg::PoseStamped>(
            "goal", 10, std::bind(&WaypointGenerator::goal_callback, this, std::placeholders::_1));
        sub_traj_start_ = this->create_subscription<geometry_msgs::msg::PoseStamped>(
            "traj_start_trigger", 10, std::bind(&WaypointGenerator::traj_start_trigger_callback, this, std::placeholders::_1));
        
        RCLCPP_INFO(this->get_logger(), "Waypoint generator initialized with type: %s", waypoint_type_.c_str());
    }

private:
    // Helper function to get yaw from quaternion
    double getYaw(const geometry_msgs::msg::Quaternion& q) {
        tf2::Quaternion tf_q(q.x, q.y, q.z, q.w);
        tf2::Matrix3x3 m(tf_q);
        double roll, pitch, yaw;
        m.getRPY(roll, pitch, yaw);
        return yaw;
    }
    
    // Helper function to create quaternion from yaw
    geometry_msgs::msg::Quaternion createQuaternionFromYaw(double yaw) {
        tf2::Quaternion q;
        q.setRPY(0, 0, yaw);
        return tf2::toMsg(q);
    }

    void load_seg(int segid, const rclcpp::Time& time_base) {
        std::string seg_str = boost::str(bfmt("seg%d.") % segid);
        double yaw;
        double time_from_start;
        
        RCLCPP_INFO(this->get_logger(), "Getting segment %d", segid);
        
        if (!this->has_parameter(seg_str + "yaw")) {
            this->declare_parameter(seg_str + "yaw", 0.0);
        }
        if (!this->has_parameter(seg_str + "time_from_start")) {
            this->declare_parameter(seg_str + "time_from_start", 0.0);
        }
        
        yaw = this->get_parameter(seg_str + "yaw").as_double();
        time_from_start = this->get_parameter(seg_str + "time_from_start").as_double();
        
        if (yaw < -3.1499999 || yaw > 3.14999999) {
            RCLCPP_ERROR(this->get_logger(), "Invalid yaw=%.3f", yaw);
            return;
        }
        if (time_from_start < 0.0) {
            RCLCPP_ERROR(this->get_logger(), "Invalid time_from_start");
            return;
        }

        std::vector<double> ptx, pty, ptz;
        
        if (!this->has_parameter(seg_str + "x")) {
            this->declare_parameter(seg_str + "x", std::vector<double>());
        }
        if (!this->has_parameter(seg_str + "y")) {
            this->declare_parameter(seg_str + "y", std::vector<double>());
        }
        if (!this->has_parameter(seg_str + "z")) {
            this->declare_parameter(seg_str + "z", std::vector<double>());
        }
        
        ptx = this->get_parameter(seg_str + "x").as_double_array();
        pty = this->get_parameter(seg_str + "y").as_double_array();
        ptz = this->get_parameter(seg_str + "z").as_double_array();

        if (ptx.empty() || ptx.size() != pty.size() || ptx.size() != ptz.size()) {
            RCLCPP_ERROR(this->get_logger(), "Invalid waypoint arrays");
            return;
        }

        nav_msgs::msg::Path path_msg;
        path_msg.header.stamp = time_base + rclcpp::Duration::from_seconds(time_from_start);

        double baseyaw = getYaw(odom_.pose.pose.orientation);
        
        for (size_t k = 0; k < ptx.size(); ++k) {
            geometry_msgs::msg::PoseStamped pt;
            pt.pose.orientation = createQuaternionFromYaw(baseyaw + yaw);
            Eigen::Vector2d dp(ptx.at(k), pty.at(k));
            Eigen::Vector2d rdp;
            rdp.x() = std::cos(-baseyaw-yaw)*dp.x() + std::sin(-baseyaw-yaw)*dp.y();
            rdp.y() =-std::sin(-baseyaw-yaw)*dp.x() + std::cos(-baseyaw-yaw)*dp.y();
            pt.pose.position.x = rdp.x() + odom_.pose.pose.position.x;
            pt.pose.position.y = rdp.y() + odom_.pose.pose.position.y;
            pt.pose.position.z = ptz.at(k) + odom_.pose.pose.position.z;
            path_msg.poses.push_back(pt);
        }

        waypoint_segments_.push_back(path_msg);
    }

    void load_waypoints(const rclcpp::Time& time_base) {
        int seg_cnt = 0;
        waypoint_segments_.clear();
        
        if (!this->has_parameter("segment_cnt")) {
            this->declare_parameter("segment_cnt", 0);
        }
        seg_cnt = this->get_parameter("segment_cnt").as_int();
        
        for (int i = 0; i < seg_cnt; ++i) {
            load_seg(i, time_base);
            if (i > 0 && waypoint_segments_.size() >= 2) {
                rclcpp::Time t1(waypoint_segments_[i - 1].header.stamp);
                rclcpp::Time t2(waypoint_segments_[i].header.stamp);
                if (t1 >= t2) {
                    RCLCPP_ERROR(this->get_logger(), "Segment timestamps not in order");
                }
            }
        }
        RCLCPP_INFO(this->get_logger(), "Overall load %zu segments", waypoint_segments_.size());
    }

    void publish_waypoints() {
        if (waypoints_.poses.empty()) return;
        
        // 发布第一个waypoint作为PoseStamped
        geometry_msgs::msg::PoseStamped waypoint_msg;
        waypoint_msg.header.frame_id = std::string("world");
        waypoint_msg.header.stamp = this->now();
        waypoint_msg.pose = waypoints_.poses[0].pose;
        pub_waypoints_->publish(waypoint_msg);
        
        geometry_msgs::msg::PoseStamped init_pose;
        init_pose.header = odom_.header;
        init_pose.pose = odom_.pose.pose;
        waypoints_.poses.insert(waypoints_.poses.begin(), init_pose);
        waypoints_.poses.clear();
    }

    void publish_waypoints_vis() {
        geometry_msgs::msg::PoseArray poseArray;
        poseArray.header.frame_id = std::string("world");
        poseArray.header.stamp = this->now();

        {
            geometry_msgs::msg::Pose init_pose;
            init_pose = odom_.pose.pose;
            poseArray.poses.push_back(init_pose);
        }

        for (auto it = waypoints_.poses.begin(); it != waypoints_.poses.end(); ++it) {
            geometry_msgs::msg::Pose p;
            p = it->pose;
            poseArray.poses.push_back(p);
        }
        pub_waypoints_vis_->publish(poseArray);
    }

    void odom_callback(const nav_msgs::msg::Odometry::SharedPtr msg) {
        is_odom_ready_ = true;
        odom_ = *msg;

        if (waypoint_segments_.size()) {
            rclcpp::Time expected_time = waypoint_segments_.front().header.stamp;
            rclcpp::Time odom_time(odom_.header.stamp);
            if (odom_time >= expected_time) {
                waypoints_ = waypoint_segments_.front();

                std::stringstream ss;
                ss << bfmt("Series send %.3f from start:\n") % (this->now() - trigged_time_).seconds();
                for (auto& pose_stamped : waypoints_.poses) {
                    ss << bfmt("P[%.2f, %.2f, %.2f] q(%.2f,%.2f,%.2f,%.2f)") %
                              pose_stamped.pose.position.x % pose_stamped.pose.position.y %
                              pose_stamped.pose.position.z % pose_stamped.pose.orientation.w %
                              pose_stamped.pose.orientation.x % pose_stamped.pose.orientation.y %
                              pose_stamped.pose.orientation.z << std::endl;
                }
                RCLCPP_INFO_STREAM(this->get_logger(), ss.str());

                publish_waypoints_vis();
                publish_waypoints();

                waypoint_segments_.pop_front();
            }
        }
    }

    void goal_callback(const geometry_msgs::msg::PoseStamped::SharedPtr msg) {
        trigged_time_ = this->now();
        
        waypoint_type_ = this->get_parameter("waypoint_type").as_string();
        
        if (waypoint_type_ == string("circle")) {
            waypoints_ = circle();
            publish_waypoints_vis();
            publish_waypoints();
        } else if (waypoint_type_ == string("eight")) {
            waypoints_ = eight();
            publish_waypoints_vis();
            publish_waypoints();
        } else if (waypoint_type_ == string("point")) {
            waypoints_ = point();
            publish_waypoints_vis();
            publish_waypoints();
        } else if (waypoint_type_ == string("series")) {
            load_waypoints(trigged_time_);
        } else if (waypoint_type_ == string("manual-lonely-waypoint")) {
            // 接受2D Goal Pose (z=0) 并设置为默认高度1.0米
            geometry_msgs::msg::PoseStamped pt = *msg;
            if (pt.pose.position.z < 0.1) {
                pt.pose.position.z = 1.0;  // 设置默认飞行高度
                RCLCPP_INFO(this->get_logger(), "Goal z adjusted to 1.0m for 2D goal");
            }
            waypoints_.poses.clear();
            waypoints_.poses.push_back(pt);
            publish_waypoints_vis();
            publish_waypoints();
        } else {
            if (msg->pose.position.z > 0) {
                geometry_msgs::msg::PoseStamped pt = *msg;
                if (waypoint_type_ == string("noyaw")) {
                    double yaw = getYaw(odom_.pose.pose.orientation);
                    pt.pose.orientation = createQuaternionFromYaw(yaw);
                }
                waypoints_.poses.push_back(pt);
                publish_waypoints_vis();
            } else if (msg->pose.position.z > -1.0) {
                if (waypoints_.poses.size() >= 1) {
                    waypoints_.poses.erase(std::prev(waypoints_.poses.end()));
                }
                publish_waypoints_vis();
            } else {
                if (waypoints_.poses.size() >= 1) {
                    publish_waypoints_vis();
                    publish_waypoints();
                }
            }
        }
    }

    void traj_start_trigger_callback(const geometry_msgs::msg::PoseStamped::SharedPtr msg) {
        if (!is_odom_ready_) {
            RCLCPP_ERROR(this->get_logger(), "No odom!");
            return;
        }

        RCLCPP_WARN(this->get_logger(), "Trigger!");
        trigged_time_ = rclcpp::Time(odom_.header.stamp);
        
        waypoint_type_ = this->get_parameter("waypoint_type").as_string();

        RCLCPP_INFO(this->get_logger(), "Pattern %s generated!", waypoint_type_.c_str());
        if (waypoint_type_ == string("free")) {
            waypoints_ = point();
            publish_waypoints_vis();
            publish_waypoints();
        } else if (waypoint_type_ == string("circle")) {
            waypoints_ = circle();
            publish_waypoints_vis();
            publish_waypoints();
        } else if (waypoint_type_ == string("eight")) {
            waypoints_ = eight();
            publish_waypoints_vis();
            publish_waypoints();
        } else if (waypoint_type_ == string("point")) {
            waypoints_ = point();
            publish_waypoints_vis();
            publish_waypoints();
        } else if (waypoint_type_ == string("series")) {
            load_waypoints(trigged_time_);
        }
    }

    // Member variables
    rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr pub_waypoints_;
    rclcpp::Publisher<geometry_msgs::msg::PoseArray>::SharedPtr pub_waypoints_vis_;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr sub_odom_;
    rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr sub_goal_;
    rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr sub_traj_start_;
    
    string waypoint_type_;
    bool is_odom_ready_;
    nav_msgs::msg::Odometry odom_;
    nav_msgs::msg::Path waypoints_;
    std::deque<nav_msgs::msg::Path> waypoint_segments_;
    rclcpp::Time trigged_time_;
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<WaypointGenerator>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}


