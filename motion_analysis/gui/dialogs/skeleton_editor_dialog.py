#!/usr/bin/env python
#
# Copyright 2019 DFKI GmbH.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the
# following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
# NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
# USE OR OTHER DEALINGS IN THE SOFTWARE.
import os
import math
import numpy as np
from copy import copy
from PySide2.QtWidgets import  QDialog, QListWidgetItem, QTableWidgetItem, QTableWidget, QFileDialog
from PySide2.QtCore import QTimer, Qt
from PySide2.QtGui import QColor
from motion_analysis.gui.layout.skeleton_editor_dialog_ui import Ui_Dialog
from .utils import get_animation_controllers
from transformations import quaternion_matrix, quaternion_multiply, quaternion_about_axis
from motion_analysis.gui.widgets.scene_viewer import SceneViewerWidget
from vis_utils.animation import load_motion_from_bvh
from vis_utils.scene.editor_scene import EditorScene
from vis_utils.animation.animation_editor import AnimationEditor
from vis_utils.io import save_json_file
from anim_utils.animation_data import BVHReader, BVHWriter, MotionVector, SkeletonBuilder
from anim_utils.retargeting.analytical import create_local_cos_map_from_skeleton_axes_with_map, find_rotation_between_vectors, OPENGL_UP_AXIS
from OpenGL.GL import *



def normalize(v):
    return v / np.linalg.norm(v)

def quaternion_from_vector_to_vector(a, b):
    """src: http://stackoverflow.com/questions/1171849/finding-quaternion-representing-the-rotation-from-one-vector-to-another
    http://wiki.ogre3d.org/Quaternion+and+Rotation+Primer"""

    v = np.cross(a, b)
    w = np.sqrt((np.linalg.norm(a) ** 2) * (np.linalg.norm(b) ** 2)) + np.dot(a, b)
    q = np.array([w, v[0], v[1], v[2]])
    if np.dot(q,q) != 0:
        return q/ np.linalg.norm(q)
    else:
        idx = np.nonzero(a)[0]
        q = np.array([0, 0, 0, 0])
        q[1 + ((idx + 1) % 2)] = 1 # [0, 0, 1, 0] for a rotation of 180 around y axis
        return q
    
def rotate_vector(q, v):
    m = quaternion_matrix(q)[:3, :3]
    v = np.dot(m, v)
    return v

X = np.array([1,0,0])
Y = np.array([0,1,0])

STANDARD_JOINTS = ["","root","pelvis", "spine_1", "spine_2", "neck", "left_clavicle", "head", "left_shoulder", "left_elbow", "left_wrist", "right_clavicle", "right_shoulder",
                    "left_hip", "left_knee", "left_ankle", "right_elbow", "right_wrist", "right_hip", "right_knee", "left_ankle", "right_ankle", "left_toe", "right_toe"]

STANDARD_JOINTS += ["left_thumb_base","left_thumb_mid", "left_thumb_tip","left_thumb_end",
                    "left_index_finger_root","left_index_finger_base","left_index_finger_mid", "left_index_finger_tip","left_index_finger_end",
                    "left_middle_finger_root","left_middle_finger_base","left_middle_finger_mid","left_middle_finger_tip","left_middle_finger_end",
                    "left_ring_finger_root","left_ring_finger_base","left_ring_finger_mid","left_ring_finger_tip", "left_ring_finger_end",
                    "left_pinky_finger_root","left_pinky_finger_base","left_pinky_finger_mid","left_pinky_finger_tip", "left_pinky_finger_end"
                   
                    "right_thumb_base","right_thumb_mid","right_thumb_tip","right_thumb_end",
                    "right_index_finger_root","right_index_finger_base","right_index_finger_mid","right_index_finger_tip","right_index_finger_end",
                    "right_middle_finger_root","right_middle_finger_base","right_middle_finger_mid","right_middle_finger_tip","right_middle_finger_end",
                    "right_ring_finger_root","right_ring_finger_base","right_ring_finger_mid","right_ring_finger_tip","right_ring_finger_end",
                    "right_pinky_finger_root","right_pinky_finger_base","right_pinky_finger_mid","right_pinky_finger_tip","right_pinky_finger_end"
                    ]
def find_key(joint_map,value):
    for key,v in joint_map.items():
        if value == v:
            return key
    return None

def axes_to_matrix_old(g_twist, g_swing, flip=False):
    q = [1, 0, 0, 0] 
    q_y = quaternion_from_vector_to_vector(Y, g_twist)
    q_y = normalize(q_y)
    q = quaternion_multiply(q_y, q)
    X_prime = rotate_vector(q_y, X)
    X_prime = normalize(X_prime)
    q_x = quaternion_from_vector_to_vector(X, g_swing)
    q_x = normalize(q_x)
    q = quaternion_multiply(q_x, q)
    q = normalize(q)
    if False:
        Y_prime = rotate_vector(q, Y)
        Y_prime = normalize(Y_prime)
        q_y2 = quaternion_from_vector_to_vector(Y_prime, g_twist)
        q_y2 = normalize(q_y2)
        q = quaternion_multiply(q_y2, q)
        q = normalize(q)
    if flip:
        q180 = quaternion_about_axis(np.deg2rad(180), g_twist)
        q180 = normalize(q180)
        q = quaternion_multiply(q180, q)
        q = normalize(q)

    m = quaternion_matrix(q)
    return m

def align_axis(a,b):
    q = quaternion_from_vector_to_vector(a, b)
    q = normalize(q)
    return q

def axes_to_matrix2(g_twist, g_swing, flip=False):
    # handle special case for the root joint
    # apply only the y axis rotation of the Hip to the Game_engine node
    not_aligned = True
    q = [1, 0, 0, 0]
    max_iter_count = 10
    iter_count = 0
    X_prime = np.array([1,0,0])
    Y_prime = np.array([0,1,0])
    while not_aligned:
        qx = align_axis(Y_prime, g_twist)  # first find rotation to align x axis
        
        q = quaternion_multiply(qx, q)
        q = normalize(q)

        X_prime = rotate_vector(q, X_prime)
        X_prime = normalize(X_prime)
        Y_prime = rotate_vector(q, Y_prime)
        Y_prime = normalize(Y_prime)

        qy  = align_axis(X_prime, g_swing)  # then add a rotation to let the y axis point up
        
        q = quaternion_multiply(qy, q)
        q = normalize(q)

        X_prime = rotate_vector(q, Y_prime)
        X_prime = normalize(Y_prime)
        Y_prime = rotate_vector(q, Y_prime)
        Y_prime = normalize(Y_prime)

        a_y = math.acos(np.dot(Y_prime, g_twist))
        a_x = math.acos(np.dot(X_prime, g_swing))
        iter_count += 1
        not_aligned = a_y > 0.1 or a_x > 0.1 and iter_count < max_iter_count
    m = quaternion_matrix(q)
    return m

def axes_to_q(g_twist, g_swing, flip=False):
    q = [1, 0, 0, 0] 
    q_y = quaternion_from_vector_to_vector(Y, g_twist)
    q_y = normalize(q_y)
    q = quaternion_multiply(q_y, q)
    X_prime = rotate_vector(q_y, X)
    X_prime = normalize(X_prime)
    q_x = quaternion_from_vector_to_vector(X_prime, g_swing)
    q_x = normalize(q_x)
    q = quaternion_multiply(q_x, q)
    q = normalize(q)
    Y_prime = rotate_vector(q, Y)
    dot = np.dot(Y_prime, g_twist)
    #dot = min(dot,1)
    dot = max(dot,-1)
    if dot == -1:
        q180 = quaternion_about_axis(np.deg2rad(180), g_swing)
        q180 = normalize(q180)
        q = quaternion_multiply(q180, q)
        q = normalize(q)
    return q


def get_spine_correction(skeleton, joint_name, up_vector):
    node = skeleton.nodes[joint_name]
    t_pose_global_m = node.get_global_matrix(skeleton.reference_frame)
    global_original = np.dot(t_pose_global_m[:3, :3], up_vector)
    global_original = normalize(global_original)

    direction_to_neck = OPENGL_UP_AXIS
    qoffset = find_rotation_between_vectors(global_original, direction_to_neck)
    return qoffset


class SkeletonEditorDialog(QDialog, Ui_Dialog):
    def __init__(self, name, skeleton, share_widget, parent=None, enable_line_edit=False, skeleton_model=None):
        QDialog.__init__(self, parent)
        Ui_Dialog.setupUi(self, self)
        self.view = SceneViewerWidget(parent, share_widget, size=(400,400))
        self.view.setObjectName("left")
        self.view.setMinimumSize(400,400)
        self.view.initializeGL()
        self.nameLineEdit.setText(name)
        self.nameLineEdit.setEnabled(enable_line_edit)
        self.name = name
        self.view.enable_mouse_interaction = True
        self.view.mouse_click.connect(self.on_mouse_click)
        self.viewerLayout.addWidget(self.view)


        self.radius = 1.5
        self.fps = 60
        self.dt = 1/60
        self.timer = QTimer()
        self.timer.timeout.connect(self.draw)
        self.timer.start(0)
        self.timer.setInterval(1000.0/self.fps)
        self.skeleton = skeleton
        self.view.makeCurrent()
        self.scene = EditorScene(True)
        self.scene.enable_scene_edit_widget = True
        
        if skeleton_model is not None:
            self.skeleton_model = skeleton_model
        elif skeleton.skeleton_model is not None:
            self.skeleton_model = skeleton.skeleton_model
        else:
            self.skeleton_model = dict()
            print("create new skeleton model")
        if "cos_map" not in self.skeleton_model:
            self.skeleton_model["cos_map"] = dict()
        if "joints" not in self.skeleton_model:
            self.skeleton_model["joints"] = dict()
        if "joint_constraints" not in self.skeleton_model:
            self.skeleton_model["joint_constraints"] = dict()

        motion_vector = MotionVector()
        self.reference_frame = skeleton.reference_frame
        print(self.reference_frame[:3])
        motion_vector.frames = [skeleton.reference_frame]
        motion_vector.n_frames = 1
        o = self.scene.object_builder.create_object("animation_controller", "skeleton", skeleton, motion_vector, skeleton.frame_time)
        self.controller = o._components["animation_controller"]
        self.skeleton = self.controller.get_skeleton()
        self.init_joints(self.controller)
        self.fill_joint_map()

        self.selectButton.clicked.connect(self.slot_accept)
        self.cancelButton.clicked.connect(self.slot_reject)
        self.applyTwistRotationButton.clicked.connect(self.slot_set_twist)
        self.applySwingRotationButton.clicked.connect(self.slot_set_swing)

        self.setOrthogonalTwistButton.clicked.connect(self.slot_set_orthogonal_twist)
        self.setOrthogonalSwingButton.clicked.connect(self.slot_set_orthogonal_swing)

        self.flipTwistButton.clicked.connect(self.slot_flip_twist)
        self.flipSwingButton.clicked.connect(self.slot_flip_swing)

        self.flipZAxisButton.clicked.connect(self.slot_flip_z_axis)
        self.alignToUpAxisButton.clicked.connect(self.slot_align_to_up_axis)

        self.setGuessButton.clicked.connect(self.slot_guess_cos_map)
        self.loadDefaultPoseButton.clicked.connect(self.slot_load_default_pose)
        self.applyScaleButton.clicked.connect(self.slot_apply_scale)
        self.jointMapComboBox.currentIndexChanged.connect(self.slot_update_joint_map)
        self.aligningRootComboBox.currentIndexChanged.connect(self.slot_update_aligning_root_joint)
        self.is_updating_joint_info = False
        self.success = False
        self.initialized = False
        self.skeleton_data = None
        self.precision = 3
        self.aligning_root_node = self.skeleton.aligning_root_node
        self.fill_root_combobox()
        self.init_aligning_root_node()


    def init_aligning_root_node(self):
        print("init",self.skeleton.root, self.skeleton.aligning_root_node)
        if self.aligning_root_node is None:
            self.aligning_root_node = self.skeleton.root
        if self.aligning_root_node is not None:
            index = self.aligningRootComboBox.findText(self.aligning_root_node, Qt.MatchFixedString)
            print("found index", index, self.aligning_root_node)
            if index >= 0:
                self.aligningRootComboBox.setCurrentIndex(index)


    def closeEvent(self, e):
         self.timer.stop()
         self.view.makeCurrent()
         del self.view


    def on_mouse_click(self, event, ray_start, ray_dir, pos, node_id):
        if event.button() == Qt.LeftButton:
            self.scene.select_object(node_id)            
            joint_knob = self.get_selected_joint()
            self.update_joint_info(joint_knob)
            
    def update_joint_info(self, joint_knob):
        self.is_updating_joint_info = True
        self.scene.scene_edit_widget.reset_rotation()
        self.jointMapComboBox.setCurrentIndex(0)
        label = "Selected Joint: "
        if joint_knob is None:
            label += "None"
            self.jointLabel.setText(label)
            self.is_updating_joint_info = False
            return

        label += joint_knob.joint_name
        joint_name = joint_knob.joint_name
        if "joints" in self.skeleton_model:
            key = find_key(self.skeleton_model["joints"], joint_name)
            print("key", joint_name, key)
            if key is not None:
                index = self.jointMapComboBox.findText(key, Qt.MatchFixedString)
                if index >= 0:
                    self.jointMapComboBox.setCurrentIndex(index)

        if "cos_map" in self.skeleton_model and joint_name in self.skeleton_model["cos_map"]:
            swing = np.round(self.skeleton_model["cos_map"][joint_name]["x"],self.precision)
            twist = np.round(self.skeleton_model["cos_map"][joint_name]["y"],self.precision)
            self.set_swing_text(swing)
            self.set_twist_text(twist)
            m = self.skeleton.nodes[joint_name].get_global_matrix(self.reference_frame)[:3,:3]
            g_swing = np.dot(m, swing)
            g_twist = np.dot(m, twist)
            
            q = axes_to_q(g_twist, g_swing)
            m = quaternion_matrix(q)
            self.scene.scene_edit_widget.rotation = m[:3,:3].T
        else:
            print("no cos map", self.skeleton_model.keys())
   
        self.jointLabel.setText(label)
        self.is_updating_joint_info = False

    def set_swing_text(self, swing):
        self.swingXLineEdit.setText(str(swing[0]))
        self.swingYLineEdit.setText(str(swing[1]))
        self.swingZLineEdit.setText(str(swing[2]))

    def set_twist_text(self, twist):
        self.twistXLineEdit.setText(str(twist[0]))
        self.twistYLineEdit.setText(str(twist[1]))
        self.twistZLineEdit.setText(str(twist[2]))

    def fill_joint_map(self):
        self.jointMapComboBox.clear()
        for idx, joint in enumerate(STANDARD_JOINTS):
            self.jointMapComboBox.addItem(joint, idx)

    def fill_root_combobox(self):
        self.aligningRootComboBox.clear()
        for idx, joint in enumerate(self.controller.get_animated_joints()):
            self.aligningRootComboBox.addItem(joint, idx)

    def init_joints(self, controller):
        for joint_name in controller.get_animated_joints():
            if len(self.skeleton.nodes[joint_name].children) > 0: # filter out end site joints
                child_node = self.skeleton.nodes[joint_name].children[0]
                if np.linalg.norm(child_node.offset)> 0:
                    self.scene.object_builder.create_object("joint_control_knob", controller, joint_name, self.radius)

    def draw(self):
        """ draw current scene on the given view
        (note before calling this function the context of the view has to be set as current using makeCurrent() and afterwards the doubble buffer has to swapped to display the current frame swapBuffers())
        """
        if not self.initialized:
            if self.view.graphics_context is not None:
                self.view.resize(400,400)
                self.initialized = True
        self.scene.update(self.dt)
        self.view.makeCurrent()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.view.graphics_context.render(self.scene)
        self.view.swapBuffers()


    def left_display_changed(self, frame_idx):
        if self.controller is not None:
            self.controller.setCurrentFrameNumber(frame_idx)
            self.leftDisplayFrameSpinBox.setValue(frame_idx)


    def left_spinbox_frame_changed(self, frame):
        self.leftStartFrameSlider.setValue(self.leftStartFrameSpinBox.value())
        self.leftEndFrameSlider.setValue(self.leftEndFrameSpinBox.value())

    def left_slider_frame_changed(self, frame):
        self.leftStartFrameSpinBox.setValue(self.leftStartFrameSlider.value())
        self.leftEndFrameSpinBox.setValue(self.leftEndFrameSlider.value())

    def slot_accept(self):
        self.name = str(self.nameLineEdit.text())
        if self.name != "":
            print("accept")
            self.success = True
            self.skeleton = self.controller.get_skeleton()
            self.skeleton.set_reference_frame(self.reference_frame)
            if self.aligning_root_node is not None:
                self.skeleton.aligning_root_node = self.aligning_root_node
            self.skeleton_data = self.skeleton.to_unity_format()
            if "cos_map" in self.skeleton_model:
                for k in self.skeleton_model["cos_map"]:
                    for l in self.skeleton_model["cos_map"][k]:
                        if type(self.skeleton_model["cos_map"][k][l]) == np.ndarray:
                            self.skeleton_model["cos_map"][k][l] = self.skeleton_model["cos_map"][k][l].tolist()
                        else:
                            self.skeleton_model["cos_map"][k][l] = self.skeleton_model["cos_map"][k][l]
            self.close()
        else:
            print("Please provide a name")

    def slot_reject(self):
        self.close()

    def get_selected_joint(self):
        joint_knob = None
        o = self.scene.selected_scene_object
        if o is not None and "joint_control_knob" in o._components:
            joint_knob = o._components["joint_control_knob"]
        return joint_knob


    def set_twist(self, joint_name):
        x = round(float(self.twistXLineEdit.text()),self.precision)
        y = round(float(self.twistYLineEdit.text()),self.precision)
        z = round(float(self.twistZLineEdit.text()),self.precision)
        #set twist axis
        twist = np.array([x,y,z])
        magnitude = np.linalg.norm(twist)
        if magnitude > 0:
            twist /= magnitude
        self.skeleton_model["cos_map"][joint_name]["y"] = twist

    def set_swing(self, joint_name):
        x = round(float(self.swingXLineEdit.text()),self.precision)
        y = round(float(self.swingYLineEdit.text()),self.precision)
        z = round(float(self.swingZLineEdit.text()),self.precision)
        #set swing axis
        swing = np.array([x,y,z])
        magnitude = np.linalg.norm(swing)
        if magnitude > 0:
            swing /= magnitude
        self.skeleton_model["cos_map"][joint_name]["x"] = swing.tolist()

    def slot_set_twist(self):
        plot = False
        joint_knob = self.get_selected_joint()
        if joint_knob is None:
            return
        self.set_swing(joint_knob.joint_name)
        self.set_twist(joint_knob.joint_name)
        self.update_joint_info(joint_knob)

    def slot_set_swing(self):
        joint_knob = self.get_selected_joint()
        if joint_knob is None:
            return
        self.set_swing(joint_knob.joint_name)
        self.set_twist(joint_knob.joint_name)
        self.update_joint_info(joint_knob)


    def slot_set_orthogonal_twist(self):
        """ https://stackoverflow.com/questions/33658620/generating-two-orthogonal-vectors-that-are-orthogonal-to-a-particular-direction """
        joint_knob = self.get_selected_joint()
        if joint_knob is None:
            return
        joint_name = joint_knob.joint_name
        #get swing axis 
        swing = np.array(self.skeleton_model["cos_map"][joint_name]["x"])
        # find orthogonal vector
        y = np.array(self.skeleton_model["cos_map"][joint_name]["y"])
        
        #y = np.random.randn(3)  # take a random vector
        y -= y.dot(swing) * swing      # make it orthogonal to twist
        y /= np.linalg.norm(y)  # normalize it

        #replace twist axis
        self.set_twist_text(y)
        self.skeleton_model["cos_map"][joint_name]["y"] = y
        self.update_joint_info(joint_knob)
        
    def slot_set_orthogonal_swing(self):
        """ https://stackoverflow.com/questions/33658620/generating-two-orthogonal-vectors-that-are-orthogonal-to-a-particular-direction """
        joint_knob = self.get_selected_joint()
        if joint_knob is None:
            return
        joint_name = joint_knob.joint_name
        #get twist axis 
        twist = np.array(self.skeleton_model["cos_map"][joint_name]["y"] )
        x = np.array(self.skeleton_model["cos_map"][joint_name]["x"] )
        x -= x.dot(twist) * twist      # make it orthogonal to twist
        x /= np.linalg.norm(x)  # normalize it
        #replace twist axis
        self.set_swing_text(x)
        self.skeleton_model["cos_map"][joint_name]["x"] = x
        self.update_joint_info(joint_knob)

    def slot_flip_twist(self):
        joint_knob = self.get_selected_joint()
        if joint_knob is None:
            return
        joint_name = joint_knob.joint_name
        #get twist axis 
        twist = np.array(self.skeleton_model["cos_map"][joint_name]["y"])
        twist *= -1
        self.skeleton_model["cos_map"][joint_name]["y"] = twist
        self.set_twist_text(twist)
        self.update_joint_info(joint_knob)

    def slot_flip_swing(self):
        joint_knob = self.get_selected_joint()
        if joint_knob is None:
            return
        joint_name = joint_knob.joint_name
        swing = np.array(self.skeleton_model["cos_map"][joint_name]["x"])
        swing *= -1
        self.skeleton_model["cos_map"][joint_name]["x"] = swing
        self.set_swing_text(swing)
        self.update_joint_info(joint_knob)

    def slot_flip_z_axis(self):
        joint_knob = self.get_selected_joint()
        if joint_knob is None:
            return
        joint_name = joint_knob.joint_name
        twist = np.array(self.skeleton_model["cos_map"][joint_name]["y"])
        swing = np.array(self.skeleton_model["cos_map"][joint_name]["x"])
        if False:
            z_axis = np.cross(twist, swing)
            z_axis *= -1
            z_axis /= np.linalg.norm(z_axis)
            new_swing = np.cross(z_axis,twist)
        if False:
            angle = np.radians(180)
            q = quaternion_about_axis(angle, twist)
            m = quaternion_matrix(q)
            swing = np.concatenate([swing,[1]])
            new_swing = np.dot(m, swing)[:3]
        new_swing = twist
        new_twist = swing
        #print("new swing", new_swing, swing)
        self.skeleton_model["cos_map"][joint_name]["y"] = new_twist
        self.skeleton_model["cos_map"][joint_name]["x"] = new_swing
        self.set_swing_text(new_swing)
        self.set_twist_text(new_twist)
        self.update_joint_info(joint_knob)

    def slot_guess_cos_map(self):
        cos_map = create_local_cos_map_from_skeleton_axes_with_map(self.skeleton)
        cos_map_copy = copy(cos_map)
        if "cos_map" in self.skeleton_model:
            cos_map.update(self.skeleton_model["cos_map"])
        
        joint_knob = self.get_selected_joint()
        joint_knob.joint_name
        cos_map[joint_knob.joint_name] = cos_map_copy[joint_knob.joint_name]
        self.skeleton_model["cos_map"] = cos_map
        self.update_joint_info(joint_knob)

    
    def slot_update_joint_map(self):
        if not self.is_updating_joint_info and "joints" in self.skeleton_model:
            joint_knob = self.get_selected_joint()
            key = str(self.jointMapComboBox.currentText())
            self.skeleton_model["joints"][key] = joint_knob.joint_name

    def slot_update_aligning_root_joint(self):
        if not self.is_updating_joint_info and "joints" in self.skeleton_model:
            self.aligning_root_node = str(self.aligningRootComboBox.currentText())


    def slot_load_default_pose(self):
        filename = QFileDialog.getOpenFileName(self, 'Load From File', '.')[0]
        filename = str(filename)
        if os.path.isfile(filename):
            motion = load_motion_from_bvh(filename)
            if len(motion.frames):
                self.reference_frame = motion.frames[0]
                frames = [self.reference_frame]
                self.controller.replace_frames(frames)
                self.controller.set_reference_frame(0)
                self.controller.updateTransformation()
                print("replaced frames")

    
    def slot_apply_scale(self):
        scale = float(self.scaleLineEdit.text())
        if scale > 0:
            self.controller.set_scale(scale)
            frames = [self.reference_frame]
            self.controller.replace_frames(frames)
            self.controller.currentFrameNumber = 0
            self.controller.updateTransformation()

    def slot_align_to_up_axis(self):
        joint_knob = self.get_selected_joint()
        if joint_knob is None:
            return
        joint_name = joint_knob.joint_name
        if joint_name in self.skeleton_model["cos_map"]:
            up_vector = self.skeleton_model["cos_map"][joint_name]["y"]
            q_offset = get_spine_correction(self.skeleton, joint_name, up_vector)
            up_vector = rotate_vector(q_offset, up_vector)
            self.skeleton_model["cos_map"][joint_name]["y"] = normalize(up_vector)
            self.update_joint_info(joint_knob)