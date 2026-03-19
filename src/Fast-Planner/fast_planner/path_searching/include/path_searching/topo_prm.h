/**
* This file is part of Fast-Planner.
*
* Copyright 2019 Boyu Zhou, Aerial Robotics Group, Hong Kong University of Science and Technology, <uav.ust.hk>
* Developed by Boyu Zhou <bzhouai at connect dot ust dot hk>, <uv dot boyuzhou at gmail dot com>
* for more information see <https://github.com/HKUST-Aerial-Robotics/Fast-Planner>.
* If you use this code, please cite the respective publications as
* listed on the above website.
*
* Fast-Planner is free software: you can redistribute it and/or modify
* it under the terms of the GNU Lesser General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* Fast-Planner is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU Lesser General Public License
* along with Fast-Planner. If not, see <http://www.gnu.org/licenses/>.
*/



#ifndef _TOPO_PRM_H
#define _TOPO_PRM_H

#include <plan_env/edt_environment.h>
#include <plan_env/raycast.h>
#include <random>

namespace fast_planner {

/* ---------- used for iterating all topo combination ---------- */
class TopoIterator {
private:
  /* data */
  vector<int> path_nums_;
  vector<int> cur_index_;
  int combine_num_;
  int cur_num_;

  void increase(int bit_num) {
    cur_index_[bit_num] += 1;
    if (cur_index_[bit_num] >= path_nums_[bit_num]) {
      cur_index_[bit_num] = 0;
      increase(bit_num + 1);
    }
  }

public:
  TopoIterator(vector<int> pn) {
    path_nums_ = pn;
    cur_index_.resize(path_nums_.size());
    fill(cur_index_.begin(), cur_index_.end(), 0);
    cur_num_ = 0;

    combine_num_ = 1;
    for (size_t i = 0; i < path_nums_.size(); ++i) {
      combine_num_ *= path_nums_[i] > 0 ? path_nums_[i] : 1;
    }
    std::cout << "[Topo]: merged path num: " << combine_num_ << std::endl;
  }
  TopoIterator() {
  }
  ~TopoIterator() {
  }

  bool nextIndex(vector<int>& index) {
    index = cur_index_;
    cur_num_ += 1;

    if (cur_num_ == combine_num_) return false;

    // go to next combination
    increase(0);
    return true;
  }
};

/* ---------- node of topo graph ---------- */
class GraphNode {
private:
  /* data */

public:
  enum NODE_TYPE { Guard = 1, Connector = 2 };

  enum NODE_STATE { NEW = 1, CLOSE = 2, OPEN = 3 };

  GraphNode(/* args */) {
  }
  GraphNode(Eigen::Vector3d pos, NODE_TYPE type, int id) {
    pos_ = pos;
    type_ = type;
    state_ = NEW;
    id_ = id;
  }
  ~GraphNode() {
  }

  vector<std::shared_ptr<GraphNode>> neighbors_;
  Eigen::Vector3d pos_;
  NODE_TYPE type_;
  NODE_STATE state_;
  int id_;

  typedef std::shared_ptr<GraphNode> Ptr;
  typedef std::shared_ptr<GraphNode> SharedPtr;
};

class TopologyPRM {
private:
  /* data */
  EDTEnvironment::Ptr edt_environment_;  // environment representation

  // sampling generator
  std::random_device rd_;
  std::default_random_engine eng_;
  std::uniform_real_distribution<double> rand_pos_;

  Eigen::Vector3d sample_r_;
  Eigen::Vector3d translation_;
  Eigen::Matrix3d rotation_;

  // roadmap data structure, 0:start, 1:goal, 2-n: others
  std::list<GraphNode::Ptr> graph_;
  std::vector<std::vector<Eigen::Vector3d>> raw_paths_;
  std::vector<std::vector<Eigen::Vector3d>> short_paths_;
  std::vector<std::vector<Eigen::Vector3d>> final_paths_;
  std::vector<Eigen::Vector3d> start_pts_, end_pts_;

  // raycasting
  std::vector<RayCaster> casters_;
  Eigen::Vector3d offset_;

  // parameter
  double max_sample_time_;
  int max_sample_num_;
  int max_raw_path_, max_raw_path2_;
  int short_cut_num_;
  Eigen::Vector3d sample_inflate_;
  double resolution_;

  double ratio_to_short_;
  int reserve_num_;

  bool parallel_shortcut_;

  /* create topological roadmap */
  /* path searching, shortening, pruning and merging */
  std::list<GraphNode::Ptr> createGraph(Eigen::Vector3d start, Eigen::Vector3d end);
  std::vector<std::vector<Eigen::Vector3d>> searchPaths();
  void shortcutPaths();
  std::vector<std::vector<Eigen::Vector3d>> pruneEquivalent(std::vector<std::vector<Eigen::Vector3d>>& paths);
  std::vector<std::vector<Eigen::Vector3d>> selectShortPaths(std::vector<std::vector<Eigen::Vector3d>>& paths, int step);

  /* ---------- helper ---------- */
  inline Eigen::Vector3d getSample();
  std::vector<GraphNode::Ptr> findVisibGuard(Eigen::Vector3d pt);  // find pairs of visibile guard
  bool needConnection(GraphNode::Ptr g1, GraphNode::Ptr g2,
                      Eigen::Vector3d pt);  // test redundancy with existing
                                            // connection between two guard
  bool lineVisib(const Eigen::Vector3d& p1, const Eigen::Vector3d& p2, double thresh,
                 Eigen::Vector3d& pc, int caster_id = 0);
  bool triangleVisib(Eigen::Vector3d pt, Eigen::Vector3d p1, Eigen::Vector3d p2);
  void pruneGraph();

  void depthFirstSearch(std::vector<GraphNode::Ptr>& vis);

  std::vector<Eigen::Vector3d> discretizeLine(Eigen::Vector3d p1, Eigen::Vector3d p2);
  std::vector<std::vector<Eigen::Vector3d>> discretizePaths(std::vector<std::vector<Eigen::Vector3d>>& path);

  std::vector<Eigen::Vector3d> discretizePath(std::vector<Eigen::Vector3d> path);
  void shortcutPath(std::vector<Eigen::Vector3d> path, int path_id, int iter_num = 1);

  std::vector<Eigen::Vector3d> discretizePath(const std::vector<Eigen::Vector3d>& path, int pt_num);
  bool sameTopoPath(const std::vector<Eigen::Vector3d>& path1, const std::vector<Eigen::Vector3d>& path2,
                    double thresh);
  Eigen::Vector3d getOrthoPoint(const std::vector<Eigen::Vector3d>& path);

  int shortestPath(std::vector<std::vector<Eigen::Vector3d>>& paths);

public:
  double clearance_;

  TopologyPRM(/* args */);
  ~TopologyPRM();

  void init(rclcpp::Node::SharedPtr nh);

  void setEnvironment(const EDTEnvironment::Ptr& env);

  void findTopoPaths(Eigen::Vector3d start, Eigen::Vector3d end, std::vector<Eigen::Vector3d> start_pts,
                     std::vector<Eigen::Vector3d> end_pts, std::list<GraphNode::Ptr>& graph,
                     std::vector<std::vector<Eigen::Vector3d>>& raw_paths,
                     std::vector<std::vector<Eigen::Vector3d>>& filtered_paths,
                     std::vector<std::vector<Eigen::Vector3d>>& select_paths);

  double pathLength(const std::vector<Eigen::Vector3d>& path);
  std::vector<Eigen::Vector3d> pathToGuidePts(std::vector<Eigen::Vector3d>& path, int pt_num);

};

}  // namespace fast_planner

#endif

