/*
 * Copyright (c) 2008, Willow Garage, Inc.
 * All rights reserved.
 */

#include <OgreManualObject.h>
#include <OgreMaterialManager.h>
#include <OgreSceneManager.h>
#include <OgreSceneNode.h>
#include <OgreTextureManager.h>

#include <rclcpp/rclcpp.hpp>
#include <rviz_common/display_context.hpp>
#include <rviz_common/frame_manager_iface.hpp>
#include <rviz_common/properties/float_property.hpp>
#include <rviz_common/properties/int_property.hpp>
#include <rviz_common/properties/property.hpp>
#include <rviz_common/properties/quaternion_property.hpp>
#include <rviz_common/properties/ros_topic_property.hpp>
#include <rviz_common/properties/vector_property.hpp>
#include <rviz_common/validate_floats.hpp>

#include "aerialmap_display.h"

namespace rviz_plugins
{

AerialMapDisplay::AerialMapDisplay()
  : manual_object_(nullptr)
  , loaded_(false)
  , resolution_(0.0f)
  , width_(0)
  , height_(0)
  , new_map_(false)
{
  topic_property_ = new rviz_common::properties::RosTopicProperty(
    "Topic", "",
    "nav_msgs/OccupancyGrid topic to subscribe to.",
    "", this, SLOT(updateTopic()), this);

  alpha_property_ = new rviz_common::properties::FloatProperty(
    "Alpha", 0.7f,
    "Amount of transparency to apply to the map.",
    this, SLOT(updateAlpha()));
  alpha_property_->setMin(0);
  alpha_property_->setMax(1);

  draw_under_property_ = new rviz_common::properties::Property(
    "Draw Behind", false,
    "Rendering option, controls whether or not the map is always"
    " drawn behind everything else.",
    this, SLOT(updateDrawUnder()), this);
}

AerialMapDisplay::~AerialMapDisplay()
{
  unsubscribe();
  clear();
}

void AerialMapDisplay::onInitialize()
{
  Display::onInitialize();
}

void AerialMapDisplay::onEnable()
{
  subscribe();
}

void AerialMapDisplay::onDisable()
{
  unsubscribe();
  clear();
}

void AerialMapDisplay::subscribe()
{
  if (!isEnabled())
    return;

  try
  {
    auto node = context_->getRosNodeAbstraction().lock();
    map_sub_ = node->get_raw_node()->create_subscription<nav_msgs::msg::OccupancyGrid>(
      topic_property_->getTopicStd(), 1,
      std::bind(&AerialMapDisplay::incomingAerialMap, this, std::placeholders::_1));
    setStatus(rviz_common::properties::StatusProperty::Ok, "Topic", "OK");
  }
  catch (rclcpp::exceptions::InvalidTopicNameError& e)
  {
    setStatus(rviz_common::properties::StatusProperty::Error, "Topic", QString("Error subscribing: ") + e.what());
  }
}

void AerialMapDisplay::unsubscribe()
{
  map_sub_.reset();
}

void AerialMapDisplay::updateTopic()
{
  unsubscribe();
  subscribe();
}

void AerialMapDisplay::updateAlpha()
{
  // Implementation for alpha update
}

void AerialMapDisplay::updateDrawUnder()
{
  // Implementation for draw under functionality
}

void AerialMapDisplay::clear()
{
  setStatus(rviz_common::properties::StatusProperty::Warn, "Message", "No map received");
  
  if (manual_object_)
  {
    scene_manager_->destroyManualObject(manual_object_);
    manual_object_ = nullptr;
  }
  
  if (texture_)
  {
    Ogre::TextureManager::getSingleton().remove(texture_->getName());
    texture_.setNull();
  }
  
  if (material_)
  {
    Ogre::MaterialManager::getSingleton().remove(material_->getName());
    material_.setNull();
  }
  
  loaded_ = false;
}

void AerialMapDisplay::incomingAerialMap(const nav_msgs::msg::OccupancyGrid::ConstSharedPtr msg)
{
  std::lock_guard<std::mutex> lock(mutex_);
  updated_map_ = msg;
  new_map_ = true;
}

void AerialMapDisplay::reset()
{
  Display::reset();
  clear();
}

void AerialMapDisplay::fixedFrameChanged()
{
  transformAerialMap();
}

void AerialMapDisplay::transformAerialMap()
{
  // Implementation for map transformation
}

void AerialMapDisplay::update(float wall_dt, float ros_dt)
{
  std::lock_guard<std::mutex> lock(mutex_);
  
  if (new_map_)
  {
    current_map_ = updated_map_;
    new_map_ = false;
    
    if (current_map_)
    {
      setStatus(rviz_common::properties::StatusProperty::Ok, "Message", 
                QString("Received aerial map %1 x %2").arg(current_map_->info.width).arg(current_map_->info.height));
    }
  }
}

} // namespace rviz_plugins

#include <pluginlib/class_list_macros.hpp>
PLUGINLIB_EXPORT_CLASS(rviz_plugins::AerialMapDisplay, rviz_common::Display)
