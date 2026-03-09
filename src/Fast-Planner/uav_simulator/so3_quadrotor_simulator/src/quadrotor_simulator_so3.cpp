#include <Eigen/Geometry>
#include <nav_msgs/msg/odometry.hpp>
#include <quadrotor_msgs/msg/so3_command.hpp>
#include <quadrotor_simulator/Quadrotor.h>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/imu.hpp>
#include <geometry_msgs/msg/vector3.hpp>
#include <uav_utils/geometry_utils.h>

typedef struct _Control {
  double rpm[4];
} Control;

typedef struct _Command {
  float force[3];
  float qx, qy, qz, qw;
  float kR[3];
  float kOm[3];
  float corrections[3];
  float current_yaw;
  bool use_external_yaw;
} Command;

typedef struct _Disturbance {
  Eigen::Vector3d f;
  Eigen::Vector3d m;
} Disturbance;

void stateToOdomMsg(const QuadrotorSimulator::Quadrotor::State& state,
                    nav_msgs::msg::Odometry& odom);
void quadToImuMsg(const QuadrotorSimulator::Quadrotor& quad,
                  sensor_msgs::msg::Imu& imu);

class QuadrotorSimulatorSO3 : public rclcpp::Node {
public:
  QuadrotorSimulatorSO3() : Node("quadrotor_simulator_so3") {
    // Declare parameters
    this->declare_parameter("simulator.init_state_x", 0.0);
    this->declare_parameter("simulator.init_state_y", 0.0);
    this->declare_parameter("simulator.init_state_z", 1.0);
    this->declare_parameter("rate.simulation", 1000.0);
    this->declare_parameter("rate.odom", 100.0);
    this->declare_parameter("quadrotor_name", "quadrotor");
    
    // Get parameters
    double init_x = this->get_parameter("simulator.init_state_x").as_double();
    double init_y = this->get_parameter("simulator.init_state_y").as_double();
    double init_z = this->get_parameter("simulator.init_state_z").as_double();
    simulation_rate_ = this->get_parameter("rate.simulation").as_double();
    double odom_rate = this->get_parameter("rate.odom").as_double();
    quad_name_ = this->get_parameter("quadrotor_name").as_string();
    
    RCLCPP_ASSERT(this->get_logger(), simulation_rate_ > 0, "Simulation rate must be positive");
    
    // Initialize quadrotor
    Eigen::Vector3d position(init_x, init_y, init_z);
    quad_.setStatePos(position);
    
    // Initialize command
    command_.force[0] = 0;
    command_.force[1] = 0;
    command_.force[2] = 0;
    command_.qx = 0;
    command_.qy = 0;
    command_.qz = 0;
    command_.qw = 1;
    command_.kR[0] = 0;
    command_.kR[1] = 0;
    command_.kR[2] = 0;
    command_.kOm[0] = 0;
    command_.kOm[1] = 0;
    command_.kOm[2] = 0;
    command_.corrections[0] = 0;
    command_.corrections[1] = 0;
    command_.corrections[2] = 0;
    command_.current_yaw = 0;
    command_.use_external_yaw = false;
    
    // Initialize disturbance
    disturbance_.f.setZero();
    disturbance_.m.setZero();
    
    // Publishers
    odom_pub_ = this->create_publisher<nav_msgs::msg::Odometry>("odom", 100);
    imu_pub_ = this->create_publisher<sensor_msgs::msg::Imu>("imu", 10);
    
    // Subscribers
    cmd_sub_ = this->create_subscription<quadrotor_msgs::msg::SO3Command>(
      "cmd", 100, std::bind(&QuadrotorSimulatorSO3::cmd_callback, this, std::placeholders::_1));
    
    f_sub_ = this->create_subscription<geometry_msgs::msg::Vector3>(
      "force_disturbance", 100, std::bind(&QuadrotorSimulatorSO3::force_disturbance_callback, this, std::placeholders::_1));
    
    m_sub_ = this->create_subscription<geometry_msgs::msg::Vector3>(
      "moment_disturbance", 100, std::bind(&QuadrotorSimulatorSO3::moment_disturbance_callback, this, std::placeholders::_1));
    
    // Initialize messages
    odom_msg_.header.frame_id = "/simulator";
    odom_msg_.child_frame_id = "/" + quad_name_;
    imu_msg_.header.frame_id = "/simulator";
    
    // Timer for simulation
    dt_ = 1.0 / simulation_rate_;
    auto timer_duration = std::chrono::duration<double>(dt_);
    sim_timer_ = this->create_wall_timer(
      timer_duration, std::bind(&QuadrotorSimulatorSO3::simulation_step, this));
    
    // Timer for publishing
    odom_pub_duration_ = std::chrono::duration<double>(1.0 / odom_rate);
    next_odom_pub_time_ = this->now();
    
    RCLCPP_INFO(this->get_logger(), "Quadrotor simulator SO3 initialized");
  }

private:
  Control getControl(const QuadrotorSimulator::Quadrotor& quad, const Command& cmd) {
    const double _kf = quad.getPropellerThrustCoefficient();
    const double _km = quad.getPropellerMomentCoefficient();
    const double kf = _kf - cmd.corrections[0];
    const double km = _km / _kf * kf;
    
    const double d = quad.getArmLength();
    const Eigen::Matrix3f J = quad.getInertia().cast<float>();
    const float I[3][3] = {
      {J(0, 0), J(0, 1), J(0, 2)},
      {J(1, 0), J(1, 1), J(1, 2)},
      {J(2, 0), J(2, 1), J(2, 2)}
    };
    const QuadrotorSimulator::Quadrotor::State state = quad.getState();
    
    // Rotation, may use external yaw
    Eigen::Vector3d _ypr = uav_utils::R_to_ypr(state.R);
    Eigen::Vector3d ypr = _ypr;
    if (cmd.use_external_yaw)
      ypr[0] = cmd.current_yaw;
    Eigen::Matrix3d R;
    R = Eigen::AngleAxisd(ypr[0], Eigen::Vector3d::UnitZ()) *
        Eigen::AngleAxisd(ypr[1], Eigen::Vector3d::UnitY()) *
        Eigen::AngleAxisd(ypr[2], Eigen::Vector3d::UnitX());
    
    float R11 = R(0, 0), R12 = R(0, 1), R13 = R(0, 2);
    float R21 = R(1, 0), R22 = R(1, 1), R23 = R(1, 2);
    float R31 = R(2, 0), R32 = R(2, 1), R33 = R(2, 2);
    float Om1 = state.omega(0), Om2 = state.omega(1), Om3 = state.omega(2);
    
    float Rd11 = cmd.qw * cmd.qw + cmd.qx * cmd.qx - cmd.qy * cmd.qy - cmd.qz * cmd.qz;
    float Rd12 = 2 * (cmd.qx * cmd.qy - cmd.qw * cmd.qz);
    float Rd13 = 2 * (cmd.qx * cmd.qz + cmd.qw * cmd.qy);
    float Rd21 = 2 * (cmd.qx * cmd.qy + cmd.qw * cmd.qz);
    float Rd22 = cmd.qw * cmd.qw - cmd.qx * cmd.qx + cmd.qy * cmd.qy - cmd.qz * cmd.qz;
    float Rd23 = 2 * (cmd.qy * cmd.qz - cmd.qw * cmd.qx);
    float Rd31 = 2 * (cmd.qx * cmd.qz - cmd.qw * cmd.qy);
    float Rd32 = 2 * (cmd.qy * cmd.qz + cmd.qw * cmd.qx);
    float Rd33 = cmd.qw * cmd.qw - cmd.qx * cmd.qx - cmd.qy * cmd.qy + cmd.qz * cmd.qz;
    
    float Psi = 0.5f * (3.0f - (Rd11 * R11 + Rd21 * R21 + Rd31 * R31 +
                                Rd12 * R12 + Rd22 * R22 + Rd32 * R32 +
                                Rd13 * R13 + Rd23 * R23 + Rd33 * R33));
    
    float force = 0;
    if (Psi < 1.0f)
      force = cmd.force[0] * R13 + cmd.force[1] * R23 + cmd.force[2] * R33;
    
    float eR1 = 0.5f * (R12 * Rd13 - R13 * Rd12 + R22 * Rd23 - R23 * Rd22 + R32 * Rd33 - R33 * Rd32);
    float eR2 = 0.5f * (R13 * Rd11 - R11 * Rd13 - R21 * Rd23 + R23 * Rd21 - R31 * Rd33 + R33 * Rd31);
    float eR3 = 0.5f * (R11 * Rd12 - R12 * Rd11 + R21 * Rd22 - R22 * Rd21 + R31 * Rd32 - R32 * Rd31);
    
    float eOm1 = Om1, eOm2 = Om2, eOm3 = Om3;
    
    float in1 = Om2 * (I[2][0] * Om1 + I[2][1] * Om2 + I[2][2] * Om3) -
                Om3 * (I[1][0] * Om1 + I[1][1] * Om2 + I[1][2] * Om3);
    float in2 = Om3 * (I[0][0] * Om1 + I[0][1] * Om2 + I[0][2] * Om3) -
                Om1 * (I[2][0] * Om1 + I[2][1] * Om2 + I[2][2] * Om3);
    float in3 = Om1 * (I[1][0] * Om1 + I[1][1] * Om2 + I[1][2] * Om3) -
                Om2 * (I[0][0] * Om1 + I[0][1] * Om2 + I[0][2] * Om3);
    
    float M1 = -cmd.kR[0] * eR1 - cmd.kOm[0] * eOm1 + in1;
    float M2 = -cmd.kR[1] * eR2 - cmd.kOm[1] * eOm2 + in2;
    float M3 = -cmd.kR[2] * eR3 - cmd.kOm[2] * eOm3 + in3;
    
    float w_sq[4];
    w_sq[0] = force / (4 * kf) - M2 / (2 * d * kf) + M3 / (4 * km);
    w_sq[1] = force / (4 * kf) + M2 / (2 * d * kf) + M3 / (4 * km);
    w_sq[2] = force / (4 * kf) + M1 / (2 * d * kf) - M3 / (4 * km);
    w_sq[3] = force / (4 * kf) - M1 / (2 * d * kf) - M3 / (4 * km);
    
    Control control;
    for (int i = 0; i < 4; i++) {
      if (w_sq[i] < 0)
        w_sq[i] = 0;
      control.rpm[i] = sqrtf(w_sq[i]);
    }
    return control;
  }
  
  void cmd_callback(const quadrotor_msgs::msg::SO3Command::SharedPtr cmd) {
    command_.force[0] = cmd->force.x;
    command_.force[1] = cmd->force.y;
    command_.force[2] = cmd->force.z;
    command_.qx = cmd->orientation.x;
    command_.qy = cmd->orientation.y;
    command_.qz = cmd->orientation.z;
    command_.qw = cmd->orientation.w;
    command_.kR[0] = cmd->k_r[0];
    command_.kR[1] = cmd->k_r[1];
    command_.kR[2] = cmd->k_r[2];
    command_.kOm[0] = cmd->k_om[0];
    command_.kOm[1] = cmd->k_om[1];
    command_.kOm[2] = cmd->k_om[2];
    command_.corrections[0] = cmd->aux.kf_correction;
    command_.corrections[1] = cmd->aux.angle_corrections[0];
    command_.corrections[2] = cmd->aux.angle_corrections[1];
    command_.current_yaw = cmd->aux.current_yaw;
    command_.use_external_yaw = cmd->aux.use_external_yaw;
  }
  
  void force_disturbance_callback(const geometry_msgs::msg::Vector3::SharedPtr f) {
    disturbance_.f(0) = f->x;
    disturbance_.f(1) = f->y;
    disturbance_.f(2) = f->z;
  }
  
  void moment_disturbance_callback(const geometry_msgs::msg::Vector3::SharedPtr m) {
    disturbance_.m(0) = m->x;
    disturbance_.m(1) = m->y;
    disturbance_.m(2) = m->z;
  }
  
  void simulation_step() {
    auto last = control_;
    control_ = getControl(quad_, command_);
    for (int i = 0; i < 4; ++i) {
      if (std::isnan(control_.rpm[i]))
        control_.rpm[i] = last.rpm[i];
    }
    
    quad_.setInput(control_.rpm[0], control_.rpm[1], control_.rpm[2], control_.rpm[3]);
    quad_.setExternalForce(disturbance_.f);
    quad_.setExternalMoment(disturbance_.m);
    quad_.step(dt_);
    
    rclcpp::Time tnow = this->now();
    if (tnow >= next_odom_pub_time_) {
      next_odom_pub_time_ = rclcpp::Time(next_odom_pub_time_.nanoseconds() + 
        std::chrono::duration_cast<std::chrono::nanoseconds>(odom_pub_duration_).count());
      
      odom_msg_.header.stamp = tnow;
      QuadrotorSimulator::Quadrotor::State state = quad_.getState();
      stateToOdomMsg(state, odom_msg_);
      quadToImuMsg(quad_, imu_msg_);
      odom_pub_->publish(odom_msg_);
      imu_pub_->publish(imu_msg_);
    }
  }
  
  QuadrotorSimulator::Quadrotor quad_;
  Command command_;
  Disturbance disturbance_;
  Control control_;
  
  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;
  rclcpp::Publisher<sensor_msgs::msg::Imu>::SharedPtr imu_pub_;
  rclcpp::Subscription<quadrotor_msgs::msg::SO3Command>::SharedPtr cmd_sub_;
  rclcpp::Subscription<geometry_msgs::msg::Vector3>::SharedPtr f_sub_;
  rclcpp::Subscription<geometry_msgs::msg::Vector3>::SharedPtr m_sub_;
  rclcpp::TimerBase::SharedPtr sim_timer_;
  
  nav_msgs::msg::Odometry odom_msg_;
  sensor_msgs::msg::Imu imu_msg_;
  
  double simulation_rate_;
  double dt_;
  std::string quad_name_;
  std::chrono::duration<double> odom_pub_duration_;
  rclcpp::Time next_odom_pub_time_;
};

void stateToOdomMsg(const QuadrotorSimulator::Quadrotor::State& state,
                    nav_msgs::msg::Odometry& odom) {
  odom.pose.pose.position.x = state.x(0);
  odom.pose.pose.position.y = state.x(1);
  odom.pose.pose.position.z = state.x(2);
  
  Eigen::Quaterniond q(state.R);
  odom.pose.pose.orientation.x = q.x();
  odom.pose.pose.orientation.y = q.y();
  odom.pose.pose.orientation.z = q.z();
  odom.pose.pose.orientation.w = q.w();
  
  odom.twist.twist.linear.x = state.v(0);
  odom.twist.twist.linear.y = state.v(1);
  odom.twist.twist.linear.z = state.v(2);
  
  odom.twist.twist.angular.x = state.omega(0);
  odom.twist.twist.angular.y = state.omega(1);
  odom.twist.twist.angular.z = state.omega(2);
}

void quadToImuMsg(const QuadrotorSimulator::Quadrotor& quad, sensor_msgs::msg::Imu& imu) {
  QuadrotorSimulator::Quadrotor::State state = quad.getState();
  Eigen::Quaterniond q(state.R);
  imu.orientation.x = q.x();
  imu.orientation.y = q.y();
  imu.orientation.z = q.z();
  imu.orientation.w = q.w();
  
  imu.angular_velocity.x = state.omega(0);
  imu.angular_velocity.y = state.omega(1);
  imu.angular_velocity.z = state.omega(2);
  
  imu.linear_acceleration.x = quad.getAcc()[0];
  imu.linear_acceleration.y = quad.getAcc()[1];
  imu.linear_acceleration.z = quad.getAcc()[2];
}

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<QuadrotorSimulatorSO3>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}

