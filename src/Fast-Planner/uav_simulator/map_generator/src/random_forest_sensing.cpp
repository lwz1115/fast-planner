#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl/kdtree/kdtree_flann.h>
#include <pcl_conversions/pcl_conversions.h>
#include <iostream>

#include <geometry_msgs/msg/pose_stamped.hpp>
#include <geometry_msgs/msg/vector3.hpp>
#include <math.h>
#include <nav_msgs/msg/odometry.hpp>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <Eigen/Eigen>
#include <random>

using namespace std;

class RandomMapSensing : public rclcpp::Node
{
public:
  RandomMapSensing() : Node("random_map_sensing")
  {
    // Publishers
    local_map_pub_ = this->create_publisher<sensor_msgs::msg::PointCloud2>("/map_generator/local_cloud", 1);
    all_map_pub_ = this->create_publisher<sensor_msgs::msg::PointCloud2>("/map_generator/global_cloud", 1);
    click_map_pub_ = this->create_publisher<sensor_msgs::msg::PointCloud2>("/pcl_render_node/local_map", 1);
    
    // Subscribers
    odom_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
      "odometry", 50, std::bind(&RandomMapSensing::rcvOdometryCallbck, this, std::placeholders::_1));
    
    // Parameters
    init_x_ = this->declare_parameter("init_state_x", 0.0);
    init_y_ = this->declare_parameter("init_state_y", 0.0);
    
    x_size_ = this->declare_parameter("map/x_size", 50.0);
    y_size_ = this->declare_parameter("map/y_size", 50.0);
    z_size_ = this->declare_parameter("map/z_size", 5.0);
    obs_num_ = this->declare_parameter("map/obs_num", 30);
    resolution_ = this->declare_parameter("map/resolution", 0.1);
    circle_num_ = this->declare_parameter("map/circle_num", 30);
    
    w_l_ = this->declare_parameter("ObstacleShape/lower_rad", 0.3);
    w_h_ = this->declare_parameter("ObstacleShape/upper_rad", 0.8);
    h_l_ = this->declare_parameter("ObstacleShape/lower_hei", 3.0);
    h_h_ = this->declare_parameter("ObstacleShape/upper_hei", 7.0);
    
    radius_l_ = this->declare_parameter("ObstacleShape/radius_l", 7.0);
    radius_h_ = this->declare_parameter("ObstacleShape/radius_h", 7.0);
    z_l_ = this->declare_parameter("ObstacleShape/z_l", 7.0);
    z_h_ = this->declare_parameter("ObstacleShape/z_h", 7.0);
    theta_ = this->declare_parameter("ObstacleShape/theta", 7.0);
    
    sensing_range_ = this->declare_parameter("sensing/radius", 10.0);
    sense_rate_ = this->declare_parameter("sensing/rate", 10.0);
    
    // Initialize parameters
    x_l_ = -x_size_ / 2.0;
    x_h_ = +x_size_ / 2.0;
    y_l_ = -y_size_ / 2.0;
    y_h_ = +y_size_ / 2.0;
    
    obs_num_ = min(obs_num_, (int)x_size_ * 10);
    z_limit_ = z_size_;
    
    map_ok_ = false;
    has_odom_ = false;
    
    // Initialize random distributions
    rand_x_ = uniform_real_distribution<double>(x_l_, x_h_);
    rand_y_ = uniform_real_distribution<double>(y_l_, y_h_);
    rand_w_ = uniform_real_distribution<double>(w_l_, w_h_);
    rand_h_ = uniform_real_distribution<double>(h_l_, h_h_);
    rand_radius_ = uniform_real_distribution<double>(radius_l_, radius_h_);
    rand_radius2_ = uniform_real_distribution<double>(radius_l_, 1.2);
    rand_theta_ = uniform_real_distribution<double>(-theta_, theta_);
    rand_z_ = uniform_real_distribution<double>(z_l_, z_h_);
    
    // Wait a bit then generate map
    rclcpp::sleep_for(std::chrono::milliseconds(500));
    RandomMapGenerate();
    
    // Create timer for publishing
    timer_ = this->create_wall_timer(
      std::chrono::milliseconds((int)(1000.0 / sense_rate_)),
      std::bind(&RandomMapSensing::pubSensedPoints, this));
  }

private:
  // Publishers and subscribers
  rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr local_map_pub_;
  rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr all_map_pub_;
  rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr click_map_pub_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;
  rclcpp::TimerBase::SharedPtr timer_;
  
  // PCL data structures
  pcl::KdTreeFLANN<pcl::PointXYZ> kdtreeLocalMap_;
  vector<int> pointIdxRadiusSearch_;
  vector<float> pointRadiusSquaredDistance_;
  pcl::PointCloud<pcl::PointXYZ> cloudMap_;
  pcl::PointCloud<pcl::PointXYZ> clicked_cloud_;
  sensor_msgs::msg::PointCloud2 globalMap_pcd_;
  sensor_msgs::msg::PointCloud2 localMap_pcd_;
  
  // Random number generation
  random_device rd_;
  default_random_engine eng_{rd_()};
  uniform_real_distribution<double> rand_x_;
  uniform_real_distribution<double> rand_y_;
  uniform_real_distribution<double> rand_w_;
  uniform_real_distribution<double> rand_h_;
  uniform_real_distribution<double> rand_radius_;
  uniform_real_distribution<double> rand_radius2_;
  uniform_real_distribution<double> rand_theta_;
  uniform_real_distribution<double> rand_z_;
  
  // State variables
  vector<double> state_;
  
  // Parameters
  int obs_num_;
  double x_size_, y_size_, z_size_;
  double x_l_, x_h_, y_l_, y_h_, w_l_, w_h_, h_l_, h_h_;
  double z_limit_, sensing_range_, resolution_, sense_rate_, init_x_, init_y_;
  bool map_ok_, has_odom_;
  int circle_num_;
  double radius_l_, radius_h_, z_l_, z_h_;
  double theta_;

  void RandomMapGenerate() {
    pcl::PointXYZ pt_random;

    // generate polar obs
    for (int i = 0; i < obs_num_; i++) {
      double x, y, w, h;
      x = rand_x_(eng_);
      y = rand_y_(eng_);
      w = rand_w_(eng_);

      if (sqrt(pow(x - init_x_, 2) + pow(y - init_y_, 2)) < 2.0) {
        i--;
        continue;
      }

      if (sqrt(pow(x - 19.0, 2) + pow(y - 0.0, 2)) < 2.0) {
        i--;
        continue;
      }

      x = floor(x / resolution_) * resolution_ + resolution_ / 2.0;
      y = floor(y / resolution_) * resolution_ + resolution_ / 2.0;

      int widNum = ceil(w / resolution_);

      for (int r = -widNum / 2.0; r < widNum / 2.0; r++)
        for (int s = -widNum / 2.0; s < widNum / 2.0; s++) {
          h = rand_h_(eng_);
          int heiNum = ceil(h / resolution_);
          for (int t = -30; t < heiNum; t++) {
            pt_random.x = x + (r + 0.5) * resolution_ + 1e-2;
            pt_random.y = y + (s + 0.5) * resolution_ + 1e-2;
            pt_random.z = (t + 0.5) * resolution_ + 1e-2;
            cloudMap_.points.push_back(pt_random);
          }
        }
    }

    // generate circle obs
    for (int i = 0; i < circle_num_; ++i) {
      double x, y, z;
      x = rand_x_(eng_);
      y = rand_y_(eng_);
      z = rand_z_(eng_);

      if (sqrt(pow(x - init_x_, 2) + pow(y - init_y_, 2)) < 2.0) {
        i--;
        continue;
      }

      if (sqrt(pow(x - 19.0, 2) + pow(y - 0.0, 2)) < 2.0) {
        i--;
        continue;
      }

      x = floor(x / resolution_) * resolution_ + resolution_ / 2.0;
      y = floor(y / resolution_) * resolution_ + resolution_ / 2.0;
      z = floor(z / resolution_) * resolution_ + resolution_ / 2.0;

      Eigen::Vector3d translate(x, y, z);

      double theta = rand_theta_(eng_);
      Eigen::Matrix3d rotate;
      rotate << cos(theta), -sin(theta), 0.0, sin(theta), cos(theta), 0.0, 0, 0, 1;

      double radius1 = rand_radius_(eng_);
      double radius2 = rand_radius2_(eng_);

      // draw a circle centered at (x,y,z)
      Eigen::Vector3d cpt;
      for (double angle = 0.0; angle < 6.282; angle += resolution_ / 2) {
        cpt(0) = 0.0;
        cpt(1) = radius1 * cos(angle);
        cpt(2) = radius2 * sin(angle);

        // inflate
        Eigen::Vector3d cpt_if;
        for (int ifx = -0; ifx <= 0; ++ifx)
          for (int ify = -0; ify <= 0; ++ify)
            for (int ifz = -0; ifz <= 0; ++ifz) {
              cpt_if = cpt + Eigen::Vector3d(ifx * resolution_, ify * resolution_, ifz * resolution_);
              cpt_if = rotate * cpt_if + Eigen::Vector3d(x, y, z);
              pt_random.x = cpt_if(0);
              pt_random.y = cpt_if(1);
              pt_random.z = cpt_if(2);
              cloudMap_.push_back(pt_random);
            }
      }
    }

    cloudMap_.width = cloudMap_.points.size();
    cloudMap_.height = 1;
    cloudMap_.is_dense = true;

    RCLCPP_WARN(this->get_logger(), "Finished generate random map ");

    kdtreeLocalMap_.setInputCloud(cloudMap_.makeShared());

    map_ok_ = true;
  }

  void rcvOdometryCallbck(const nav_msgs::msg::Odometry::SharedPtr odom) {
    if (odom->child_frame_id == "X" || odom->child_frame_id == "O") return;
    has_odom_ = true;

    state_ = {odom->pose.pose.position.x,
              odom->pose.pose.position.y,
              odom->pose.pose.position.z,
              odom->twist.twist.linear.x,
              odom->twist.twist.linear.y,
              odom->twist.twist.linear.z,
              0.0,
              0.0,
              0.0};
  }

  void pubSensedPoints() {
    // if (i < 10) {
    pcl::toROSMsg(cloudMap_, globalMap_pcd_);
    globalMap_pcd_.header.frame_id = "world";
    all_map_pub_->publish(globalMap_pcd_);
    // }

    return;

    /* ---------- only publish points around current position ---------- */
    if (!map_ok_ || !has_odom_) return;

    pcl::PointCloud<pcl::PointXYZ> localMap;

    pcl::PointXYZ searchPoint(state_[0], state_[1], state_[2]);
    pointIdxRadiusSearch_.clear();
    pointRadiusSquaredDistance_.clear();

    pcl::PointXYZ pt;

    if (isnan(searchPoint.x) || isnan(searchPoint.y) || isnan(searchPoint.z))
      return;

    if (kdtreeLocalMap_.radiusSearch(searchPoint, sensing_range_,
                                    pointIdxRadiusSearch_,
                                    pointRadiusSquaredDistance_) > 0) {
      for (size_t i = 0; i < pointIdxRadiusSearch_.size(); ++i) {
        pt = cloudMap_.points[pointIdxRadiusSearch_[i]];
        localMap.points.push_back(pt);
      }
    } else {
      RCLCPP_ERROR(this->get_logger(), "[Map server] No obstacles .");
      return;
    }

    localMap.width = localMap.points.size();
    localMap.height = 1;
    localMap.is_dense = true;

    pcl::toROSMsg(localMap, localMap_pcd_);
    localMap_pcd_.header.frame_id = "world";
    local_map_pub_->publish(localMap_pcd_);
  }

  void clickCallback(const geometry_msgs::msg::PoseStamped::SharedPtr msg) {
    double x = msg->pose.position.x;
    double y = msg->pose.position.y;
    double w = rand_w_(eng_);
    double h;
    pcl::PointXYZ pt_random;

    x = floor(x / resolution_) * resolution_ + resolution_ / 2.0;
    y = floor(y / resolution_) * resolution_ + resolution_ / 2.0;

    int widNum = ceil(w / resolution_);

    for (int r = -widNum / 2.0; r < widNum / 2.0; r++)
      for (int s = -widNum / 2.0; s < widNum / 2.0; s++) {
        h = rand_h_(eng_);
        int heiNum = ceil(h / resolution_);
        for (int t = -1; t < heiNum; t++) {
          pt_random.x = x + (r + 0.5) * resolution_ + 1e-2;
          pt_random.y = y + (s + 0.5) * resolution_ + 1e-2;
          pt_random.z = (t + 0.5) * resolution_ + 1e-2;
          clicked_cloud_.points.push_back(pt_random);
          cloudMap_.points.push_back(pt_random);
        }
      }
    clicked_cloud_.width = clicked_cloud_.points.size();
    clicked_cloud_.height = 1;
    clicked_cloud_.is_dense = true;

    pcl::toROSMsg(clicked_cloud_, localMap_pcd_);
    localMap_pcd_.header.frame_id = "world";
    click_map_pub_->publish(localMap_pcd_);

    cloudMap_.width = cloudMap_.points.size();

    return;
  }
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<RandomMapSensing>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
