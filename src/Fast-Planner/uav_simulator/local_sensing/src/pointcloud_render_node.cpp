#include <nav_msgs/msg/odometry.hpp>
#include <nav_msgs/msg/path.hpp>
#include <pcl/filters/voxel_grid.h>
#include <pcl/kdtree/kdtree_flann.h>
#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl/search/kdtree.h>
#include <pcl_conversions/pcl_conversions.h>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <Eigen/Dense>
#include <fstream>
#include <iostream>
#include <pcl/search/impl/kdtree.hpp>
#include <vector>

using namespace std;
using namespace Eigen;

class PointCloudRenderNode : public rclcpp::Node {
public:
  PointCloudRenderNode() : Node("pcl_render") {
    // Declare parameters
    this->declare_parameter("sensing_horizon", 5.0);
    this->declare_parameter("sensing_rate", 10.0);
    this->declare_parameter("estimation_rate", 10.0);
    this->declare_parameter("map.x_size", 40.0);
    this->declare_parameter("map.y_size", 40.0);
    this->declare_parameter("map.z_size", 5.0);
    this->declare_parameter("map.resolution", 0.1);
    
    // Get parameters
    sensing_horizon_ = this->get_parameter("sensing_horizon").as_double();
    sensing_rate_ = this->get_parameter("sensing_rate").as_double();
    estimation_rate_ = this->get_parameter("estimation_rate").as_double();
    x_size_ = this->get_parameter("map.x_size").as_double();
    y_size_ = this->get_parameter("map.y_size").as_double();
    z_size_ = this->get_parameter("map.z_size").as_double();
    resolution_ = this->get_parameter("map.resolution").as_double();
    
    inv_resolution_ = 1.0 / resolution_;
    gl_xl_ = -x_size_ / 2.0;
    gl_yl_ = -y_size_ / 2.0;
    gl_zl_ = 0.0;
    
    GLX_SIZE_ = (int)(x_size_ * inv_resolution_);
    GLY_SIZE_ = (int)(y_size_ * inv_resolution_);
    GLZ_SIZE_ = (int)(z_size_ * inv_resolution_);
    
    // Subscribers
    global_map_sub_ = this->create_subscription<sensor_msgs::msg::PointCloud2>(
      "global_map", 1, std::bind(&PointCloudRenderNode::rcvGlobalPointCloudCallBack, this, std::placeholders::_1));
    
    local_map_sub_ = this->create_subscription<sensor_msgs::msg::PointCloud2>(
      "local_map", 1, std::bind(&PointCloudRenderNode::rcvLocalPointCloudCallBack, this, std::placeholders::_1));
    
    odom_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
      "odometry", 50, std::bind(&PointCloudRenderNode::rcvOdometryCallbck, this, std::placeholders::_1));
    
    // Publisher
    pub_cloud_ = this->create_publisher<sensor_msgs::msg::PointCloud2>("/pcl_render_node/cloud", 10);
    
    // Timer
    double sensing_duration = 1.0 / sensing_rate_ * 2.5;
    local_sensing_timer_ = this->create_wall_timer(
      std::chrono::duration<double>(sensing_duration),
      std::bind(&PointCloudRenderNode::renderSensedPoints, this));
    
    RCLCPP_INFO(this->get_logger(), "PointCloud render node initialized");
  }

private:
  // Subscribers
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;
  rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr global_map_sub_;
  rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr local_map_sub_;
  
  // Publisher
  rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr pub_cloud_;
  
  // Timer
  rclcpp::TimerBase::SharedPtr local_sensing_timer_;
  
  // State flags
  bool has_global_map_ = false;
  bool has_local_map_ = false;
  bool has_odom_ = false;
  
  // Data
  nav_msgs::msg::Odometry odom_;
  pcl::PointCloud<pcl::PointXYZ> cloud_all_map_;
  pcl::PointCloud<pcl::PointXYZ> local_map_;
  pcl::VoxelGrid<pcl::PointXYZ> voxel_sampler_;
  sensor_msgs::msg::PointCloud2 local_map_pcd_;
  pcl::search::KdTree<pcl::PointXYZ> kdtree_local_map_;
  vector<int> point_idx_radius_search_;
  vector<float> point_radius_squared_distance_;
  
  // Parameters
  double sensing_horizon_;
  double sensing_rate_;
  double estimation_rate_;
  double x_size_, y_size_, z_size_;
  double gl_xl_, gl_yl_, gl_zl_;
  double resolution_, inv_resolution_;
  int GLX_SIZE_, GLY_SIZE_, GLZ_SIZE_;
  
  inline Eigen::Vector3d gridIndex2coord(const Eigen::Vector3i& index) {
    Eigen::Vector3d pt;
    pt(0) = ((double)index(0) + 0.5) * resolution_ + gl_xl_;
    pt(1) = ((double)index(1) + 0.5) * resolution_ + gl_yl_;
    pt(2) = ((double)index(2) + 0.5) * resolution_ + gl_zl_;
    return pt;
  }
  
  inline Eigen::Vector3i coord2gridIndex(const Eigen::Vector3d& pt) {
    Eigen::Vector3i idx;
    idx(0) = std::min(std::max(int((pt(0) - gl_xl_) * inv_resolution_), 0), GLX_SIZE_ - 1);
    idx(1) = std::min(std::max(int((pt(1) - gl_yl_) * inv_resolution_), 0), GLY_SIZE_ - 1);
    idx(2) = std::min(std::max(int((pt(2) - gl_zl_) * inv_resolution_), 0), GLZ_SIZE_ - 1);
    return idx;
  }
  
  void rcvOdometryCallbck(const nav_msgs::msg::Odometry::SharedPtr odom) {
    has_odom_ = true;
    odom_ = *odom;
  }
  
  void rcvGlobalPointCloudCallBack(const sensor_msgs::msg::PointCloud2::SharedPtr pointcloud_map) {
    if (has_global_map_) return;
    
    RCLCPP_WARN(this->get_logger(), "Global Pointcloud received..");
    
    pcl::PointCloud<pcl::PointXYZ> cloud_input;
    pcl::fromROSMsg(*pointcloud_map, cloud_input);
    
    voxel_sampler_.setLeafSize(0.1f, 0.1f, 0.1f);
    voxel_sampler_.setInputCloud(cloud_input.makeShared());
    voxel_sampler_.filter(cloud_all_map_);
    
    kdtree_local_map_.setInputCloud(cloud_all_map_.makeShared());
    
    has_global_map_ = true;
  }
  
  void renderSensedPoints() {
    if (!has_global_map_ || !has_odom_) return;
    
    Eigen::Quaterniond q;
    q.x() = odom_.pose.pose.orientation.x;
    q.y() = odom_.pose.pose.orientation.y;
    q.z() = odom_.pose.pose.orientation.z;
    q.w() = odom_.pose.pose.orientation.w;
    
    Eigen::Matrix3d rot;
    rot = q;
    Eigen::Vector3d yaw_vec = rot.col(0);
    
    local_map_.points.clear();
    pcl::PointXYZ searchPoint(odom_.pose.pose.position.x,
                              odom_.pose.pose.position.y,
                              odom_.pose.pose.position.z);
    point_idx_radius_search_.clear();
    point_radius_squared_distance_.clear();
    
    pcl::PointXYZ pt;
    if (kdtree_local_map_.radiusSearch(searchPoint, sensing_horizon_,
                                       point_idx_radius_search_,
                                       point_radius_squared_distance_) > 0) {
      for (size_t i = 0; i < point_idx_radius_search_.size(); ++i) {
        pt = cloud_all_map_.points[point_idx_radius_search_[i]];
        
        if ((fabs(pt.z - odom_.pose.pose.position.z) / (sensing_horizon_)) > tan(M_PI / 12.0))
          continue;
        
        Vector3d pt_vec(pt.x - odom_.pose.pose.position.x,
                        pt.y - odom_.pose.pose.position.y,
                        pt.z - odom_.pose.pose.position.z);
        
        if (pt_vec.dot(yaw_vec) < 0) continue;
        
        local_map_.points.push_back(pt);
      }
    } else {
      return;
    }
    
    local_map_.width = local_map_.points.size();
    local_map_.height = 1;
    local_map_.is_dense = true;
    
    pcl::toROSMsg(local_map_, local_map_pcd_);
    local_map_pcd_.header.frame_id = "map";
    local_map_pcd_.header.stamp = this->now();
    
    pub_cloud_->publish(local_map_pcd_);
  }
  
  void rcvLocalPointCloudCallBack(const sensor_msgs::msg::PointCloud2::SharedPtr pointcloud_map) {
    // do nothing, fix later
  }
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<PointCloudRenderNode>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}

