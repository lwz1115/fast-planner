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
#include <rviz_common/properties/property.hpp>
#include <rviz_common/properties/ros_topic_property.hpp>
#include <rviz_common/validate_floats.hpp>

#include "multi_probmap_display.h"

namespace rviz_plugins
{

MultiProbMapDisplay::MultiProbMapDisplay()
  : loaded_(false)
  , new_map_(false)
{
  topic_property_ = new rviz_common::properties::RosTopicProperty(
    "Topic", "",
    "multi_map_server/MultiOccupancyGrid topic to subscribe to.",
    "", this, SLOT(updateTopic()), this);

  draw_under_property_ = new rviz_common::properties::Property(
    "Draw Behind", false,
    "Rendering option, controls whether or not the map is always"
    " drawn behind everything else.",
    this, SLOT(updateDrawUnder()), this);
}

MultiProbMapDisplay::~MultiProbMapDisplay()
{
  unsubscribe();
  clear();
}

void MultiProbMapDisplay::onInitialize()
{
  Display::onInitialize();
}

void MultiProbMapDisplay::onEnable()
{
  subscribe();
}

void MultiProbMapDisplay::onDisable()
{
  unsubscribe();
  clear();
}

void MultiProbMapDisplay::subscribe()
{
  if (!isEnabled())
    return;

  try
  {
    auto node = context_->getRosNodeAbstraction().lock();
    map_sub_ = node->get_raw_node()->create_subscription<multi_map_server::msg::MultiOccupancyGrid>(
      topic_property_->getTopicStd(), 1,
      std::bind(&MultiProbMapDisplay::incomingMap, this, std::placeholders::_1));
    setStatus(rviz_common::properties::StatusProperty::Ok, "Topic", "OK");
  }
  catch (rclcpp::exceptions::InvalidTopicNameError& e)
  {
    setStatus(rviz_common::properties::StatusProperty::Error, "Topic", QString("Error subscribing: ") + e.what());
  }
}

void MultiProbMapDisplay::unsubscribe()
{
  map_sub_.reset();
}

void MultiProbMapDisplay::updateTopic()
{
  unsubscribe();
  subscribe();
}

void MultiProbMapDisplay::updateDrawUnder()
{
  // Implementation for draw under functionality
}

void MultiProbMapDisplay::clear()
{
  setStatus(rviz_common::properties::StatusProperty::Warn, "Message", "No map received");
  
  for (auto& obj : manual_object_)
  {
    if (obj)
    {
      scene_manager_->destroyManualObject(obj);
    }
  }
  manual_object_.clear();
  
  for (auto& tex : texture_)
  {
    if (tex)
    {
      Ogre::TextureManager::getSingleton().remove(tex->getName());
    }
  }
  texture_.clear();
  
  for (auto& mat : material_)
  {
    if (mat)
    {
      Ogre::MaterialManager::getSingleton().remove(mat->getName());
    }
  }
  material_.clear();
  
  loaded_ = false;
}

void MultiProbMapDisplay::incomingMap(const multi_map_server::msg::MultiOccupancyGrid::SharedPtr msg)
{
  std::lock_guard<std::mutex> lock(mutex_);
  updated_map_ = msg;
  new_map_ = true;
}

void MultiProbMapDisplay::reset()
{
  Display::reset();
  clear();
}

void MultiProbMapDisplay::update(float wall_dt, float ros_dt)
{
  std::lock_guard<std::mutex> lock(mutex_);
  
  if (new_map_)
  {
    current_map_ = updated_map_;
    new_map_ = false;
    
    // Simple implementation - just set status
    if (current_map_)
    {
      setStatus(rviz_common::properties::StatusProperty::Ok, "Message", 
                QString("Received %1 maps").arg(current_map_->maps.size()));
    }
  }
}

} // namespace rviz_plugins

#include <pluginlib/class_list_macros.hpp>
PLUGINLIB_EXPORT_CLASS(rviz_plugins::MultiProbMapDisplay, rviz_common::Display)
