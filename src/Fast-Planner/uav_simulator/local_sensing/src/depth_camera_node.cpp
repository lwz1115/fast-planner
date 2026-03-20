#include <nav_msgs/msg/odometry.hpp>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <cv_bridge/cv_bridge.h>
#include <opencv2/opencv.hpp>
#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl_conversions/pcl_conversions.h>
#include <Eigen/Dense>

class DepthCameraNode : public rclcpp::Node {
public:
  DepthCameraNode() : Node("depth_camera") {
    // Camera parameters
    this->declare_parameter("cam_width", 640);
    this->declare_parameter("cam_height", 480);
    this->declare_parameter("cam_fx", 387.229248046875);
    this->declare_parameter("cam_fy", 387.229248046875);
    this->declare_parameter("cam_cx", 321.04638671875);
    this->declare_parameter("cam_cy", 243.44969177246094);
    this->declare_parameter("max_depth", 10.0);
    
    cam_width_ = this->get_parameter("cam_width").as_int();
    cam_height_ = this->get_parameter("cam_height").as_int();
    cam_fx_ = this->get_parameter("cam_fx").as_double();
    cam_fy_ = this->get_parameter("cam_fy").as_double();
    cam_cx_ = this->get_parameter("cam_cx").as_double();
    cam_cy_ = this->get_parameter("cam_cy").as_double();
    max_depth_ = this->get_parameter("max_depth").as_double();
    
    // Subscribers
    cloud_sub_ = this->create_subscription<sensor_msgs::msg::PointCloud2>(
      "point_cloud", 10, std::bind(&DepthCameraNode::cloudCallback, this, std::placeholders::_1));
    
    odom_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
      "odometry", 10, std::bind(&DepthCameraNode::odomCallback, this, std::placeholders::_1));
    
    // Publishers
    depth_pub_ = this->create_publisher<sensor_msgs::msg::Image>("depth", 10);
    color_depth_pub_ = this->create_publisher<sensor_msgs::msg::Image>("color_depth", 10);
    
    RCLCPP_INFO(this->get_logger(), "Depth camera node initialized");
  }

private:
  // Subscribers
  rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr cloud_sub_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;
  
  // Publishers
  rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr depth_pub_;
  rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr color_depth_pub_;
  
  // State
  bool has_odom_ = false;
  nav_msgs::msg::Odometry odom_;
  
  // Camera parameters
  int cam_width_, cam_height_;
  double cam_fx_, cam_fy_, cam_cx_, cam_cy_;
  double max_depth_;
  
  void odomCallback(const nav_msgs::msg::Odometry::SharedPtr msg) {
    odom_ = *msg;
    has_odom_ = true;
  }
  
  void cloudCallback(const sensor_msgs::msg::PointCloud2::SharedPtr msg) {
    if (!has_odom_) return;
    
    // Convert to PCL
    pcl::PointCloud<pcl::PointXYZ> cloud;
    pcl::fromROSMsg(*msg, cloud);
    
    if (cloud.empty()) return;
    
    // Get camera pose from odometry
    Eigen::Quaterniond q(
      odom_.pose.pose.orientation.w,
      odom_.pose.pose.orientation.x,
      odom_.pose.pose.orientation.y,
      odom_.pose.pose.orientation.z
    );
    Eigen::Matrix3d R_w2c = q.toRotationMatrix().transpose();
    Eigen::Vector3d t_w(
      odom_.pose.pose.position.x,
      odom_.pose.pose.position.y,
      odom_.pose.pose.position.z
    );
    
    // Create depth image
    cv::Mat depth_img(cam_height_, cam_width_, CV_32FC1, cv::Scalar(0.0f));
    
    // 膨胀半径：距离越近点越大
    for (const auto& pt : cloud.points) {
      Eigen::Vector3d pw(pt.x, pt.y, pt.z);
      Eigen::Vector3d pc = R_w2c * (pw - t_w);
      
      double depth = pc.x();
      if (depth <= 0.1 || depth > max_depth_) continue;
      
      int u = static_cast<int>(cam_fx_ * pc.y() / depth + cam_cx_);
      int v = static_cast<int>(cam_fy_ * (-pc.z()) / depth + cam_cy_);
      
      if (u < 0 || u >= cam_width_ || v < 0 || v >= cam_height_) continue;
      
      // 根据深度动态调整膨胀半径（近大远小）
      int radius = std::max(1, static_cast<int>(8.0 / depth));
      radius = std::min(radius, 8);
      
      for (int dv = -radius; dv <= radius; ++dv) {
        for (int du = -radius; du <= radius; ++du) {
          int nu = u + du, nv = v + dv;
          if (nu < 0 || nu >= cam_width_ || nv < 0 || nv >= cam_height_) continue;
          float& d = depth_img.at<float>(nv, nu);
          if (d == 0.0f || depth < d) d = static_cast<float>(depth);
        }
      }
    }
    
    auto stamp = this->now();
    
    // Publish raw depth image (32FC1)
    auto depth_msg = cv_bridge::CvImage(std_msgs::msg::Header(), "32FC1", depth_img).toImageMsg();
    depth_msg->header.stamp = stamp;
    depth_msg->header.frame_id = "camera";
    depth_pub_->publish(*depth_msg);
    
    // Create and publish color depth image for visualization
    cv::Mat depth_norm, depth_color;
    cv::normalize(depth_img, depth_norm, 0, 255, cv::NORM_MINMAX, CV_8UC1);
    cv::applyColorMap(depth_norm, depth_color, cv::COLORMAP_JET);
    depth_color.setTo(cv::Scalar(0, 0, 0), depth_img == 0.0f);
    
    auto color_msg = cv_bridge::CvImage(std_msgs::msg::Header(), "bgr8", depth_color).toImageMsg();
    color_msg->header.stamp = stamp;
    color_msg->header.frame_id = "camera";
    color_depth_pub_->publish(*color_msg);
  }
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<DepthCameraNode>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
