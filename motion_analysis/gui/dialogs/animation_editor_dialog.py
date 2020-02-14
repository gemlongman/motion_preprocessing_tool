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
import numpy as np
from PySide2.QtCore import QTimer, Qt
from PySide2.QtWidgets import QDialog, QListWidgetItem, QTableWidgetItem, QTableWidget, QFileDialog
from PySide2.QtGui import QColor
from motion_analysis.gui.layout.animation_editor_dialog_ui import Ui_Dialog
from motion_analysis.gui.dialogs import SelectSceneObjectsDialog
from .utils import get_animation_controllers
from motion_analysis.gui.widgets.scene_viewer import SceneViewerWidget
from vis_utils.scene.editor_scene import EditorScene
from vis_utils.animation.animation_editor import AnimationEditor
from vis_utils.io import save_json_file
from OpenGL.GL import *




class AnimationEditorDialog(QDialog, Ui_Dialog):
    def __init__(self, controller, scene, share_widget, parent=None):
        QDialog.__init__(self, parent)
        Ui_Dialog.setupUi(self, self)
        self.leftView = SceneViewerWidget(parent, share_widget, size=(400,400))
        self.leftView.setObjectName("left")
        self.leftView.setMinimumSize(400,400)
        self.leftView.initializeGL()
        self.leftView.enable_mouse_interaction = True
        self.leftView.mouse_click.connect(self.on_mouse_click)
        self.leftViewerLayout.addWidget(self.leftView)


        self.radius = 1.5
        self.fps = 60
        self.dt = 1/60
        self.timer = QTimer()
        self.timer.timeout.connect(self.draw)
        self.timer.start(0)
        self.timer.setInterval(1000.0/self.fps)
        self.scene = scene
        self.original_controller = controller
        self.left_controller = None
        self.skeleton = None
        self.leftView.makeCurrent()
        self.left_scene = EditorScene(True)
        self.left_scene.enable_scene_edit_widget = False
        self._animation_editor = None
        if controller is not None:
            self.left_controller = self.copy_controller(controller, self.left_scene)
            fps = int(1.0 / self.left_controller._motion.mv.frame_time)
            self.fpsLineEdit.setText(str(fps))
            self.skeleton = self.left_controller.get_skeleton()
            n_frames = self.left_controller.getNumberOfFrames()
            self.init_joints(self.left_controller)
        else:
            n_frames = 0
        
        self.controllers = dict()
        
        self.selectButton.clicked.connect(self.slot_accept)
        self.cancelButton.clicked.connect(self.slot_reject)

        self.deleteBeforeButton.clicked.connect(self.slot_delete_frames_before)
        self.deleteAfterButton.clicked.connect(self.slot_delete_frames_after)
        self.concatenateButton.clicked.connect(self.slot_concatenate)
        self.translateJointButton.clicked.connect(self.slot_translate_joint)
        self.rotateJointButton.clicked.connect(self.slot_rotate_joint)
        self.smoothFramesButton.clicked.connect(self.slot_smooth_frames)
        self.mirrorAnimationButton.clicked.connect(self.slot_mirror_animation)
        self.fixJointButton.clicked.connect(self.slot_fix_joint)
        self.clearConstraintsButton.clicked.connect(self.slot_clear_constraints)
        self.undoButton.clicked.connect(self.slot_undo)
        self.exportCommandsButton.clicked.connect(self.slot_export_command_history)
        self.applyConstraintsButton.clicked.connect(self.slot_apply_constraints)
        self.resampleButton.clicked.connect(self.slot_resample_motion)
        self.setFPSButton.clicked.connect(self.slot_set_fps)
        self.flipBlenderCoordinateSystemButton.clicked.connect(self.flip_blender_coordinate_systems)


        self.leftStartFrameSlider.valueChanged.connect(self.left_slider_frame_changed)
        self.leftEndFrameSlider.valueChanged.connect(self.left_slider_frame_changed)
        self.leftStartFrameSpinBox.valueChanged.connect(self.left_spinbox_frame_changed)
        self.leftEndFrameSpinBox.valueChanged.connect(self.left_spinbox_frame_changed)


        self.leftDisplayFrameSlider.valueChanged.connect(self.left_display_changed)
        self.leftDisplayFrameSpinBox.valueChanged.connect(self.left_display_changed)
        #self.close.triggered.connect(self.on_close)

        self.guessGroundHeightButton.clicked.connect(self.guess_ground_height)
        self.moveToGroundButton.clicked.connect(self.move_to_ground)

        self.success = False
        self.n_frames = n_frames
        self.start_frame = 0
        self.end_frame = n_frames-1#
        self.set_frame_range()
        self.initialized = False
        self.collect_constraints = True
        self.original_frames = np.array(self.left_controller.get_frames())

    def closeEvent(self, e):
        self.timer.stop()
        self.leftView.makeCurrent()
        try:
           del self.leftView
        except:
            print("ignore the error and keep going")


    def slot_undo(self):
        frames = self._animation_editor.undo()
        if frames is not None:
            self.n_frames = len(frames)
            self.set_frame_range()
            self.original_controller.replace_frames(frames)
            self.original_controller.updateTransformation()
            print("undo")
        else:
            print("nothing to undo")

    def on_mouse_click(self, event, ray_start, ray_dir, pos, node_id):
        if event.button() == Qt.LeftButton:
            self.left_scene.select_object(node_id)            
            joint_knob = self.get_selected_joint()
            label = "Selected Joint: "
            if joint_knob is not None:
                label += joint_knob.joint_name
            else:
                label += "None"
            self.jointLabel.setText(label)


    def init_joints(self, controller):
        for joint_name in controller.get_animated_joints():
            if len(self.skeleton.nodes[joint_name].children) > 0: # filter out end site joints
                child_node = self.skeleton.nodes[joint_name].children[0]
                if np.linalg.norm(child_node.offset)> 0:
                    self.left_scene.object_builder.create_object("joint_control_knob", controller, joint_name, self.radius)
         

    def copy_controller(self, controller, target_scene):
        skeleton = controller.get_skeleton_copy()
        mv = controller.get_motion_vector_copy()
        print("copied", mv.n_frames, len(mv.frames), controller.getNumberOfFrames())
        o = target_scene.object_builder.create_object("animation_controller","", 
                                            skeleton, mv, mv.frame_time, 
                                            semantic_annotation=None) 
        
        #target_scene.object_builder.create_component("animation_editor", o)
        self._animation_editor = AnimationEditor(o) #o._components["animation_editor"]
        return o._components["animation_controller"]


    def draw(self):
        """ draw current scene on the given view
        (note before calling this function the context of the view has to be set as current using makeCurrent() and afterwards the doubble buffer has to swapped to display the current frame swapBuffers())
        """
        if not self.initialized:
            if self.leftView.graphics_context is not None:
                self.leftView.resize(400,400)
                self.initialized = True
        self.left_scene.update(self.dt)
        self.leftView.makeCurrent()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.leftView.graphics_context.render(self.left_scene)
        self.leftView.swapBuffers()


    def left_display_changed(self, frame_idx):
        if self.left_controller is not None:
            self.left_controller.setCurrentFrameNumber(frame_idx)
            self.leftDisplayFrameSpinBox.setValue(frame_idx)


    def left_spinbox_frame_changed(self, frame):
        self.leftStartFrameSlider.setValue(self.leftStartFrameSpinBox.value())
        self.leftEndFrameSlider.setValue(self.leftEndFrameSpinBox.value())

    def left_slider_frame_changed(self, frame):
        self.leftStartFrameSpinBox.setValue(self.leftStartFrameSlider.value())
        self.leftEndFrameSpinBox.setValue(self.leftEndFrameSlider.value())

    def slot_accept(self):
        self.success = True
        self.close()

    def slot_reject(self):
        self.close()


    def set_frame_range(self):
        self.leftDisplayFrameSlider.setRange(0, self.n_frames-1)
        self.leftDisplayFrameSpinBox.setRange(0, self.n_frames-1)

        self.leftStartFrameSlider.setRange(0, self.n_frames-1)
        self.leftEndFrameSlider.setRange(0, self.n_frames-1)
        self.leftStartFrameSpinBox.setRange(0, self.n_frames-1)
        self.leftEndFrameSpinBox.setRange(0, self.n_frames-1)

        self.leftEndFrameSlider.setValue(self.n_frames - 1)
        self.leftEndFrameSpinBox.setValue(self.n_frames - 1)

    def get_selected_joint(self):
        joint_knob = None
        o = self.left_scene.selected_scene_object
        if o is not None and "joint_control_knob" in o._components:
            joint_knob = o._components["joint_control_knob"]
        return joint_knob

    def slot_translate_joint(self):
        plot = False
        joint_knob = self.get_selected_joint()
        if joint_knob is None:
            return
        x = float(self.translateXLineEdit.text())
        y = float(self.translateYLineEdit.text())
        z = float(self.translateZLineEdit.text())
        offset = [x,y,z]
        joint_name = joint_knob.joint_name
        edit_start = self.leftStartFrameSlider.value()
        edit_end = self.leftEndFrameSlider.value()+1 
        if edit_start > edit_end:
            print("frame range is wrong", edit_start, edit_end)
            return
        frame_range = edit_start, edit_end

        joint_knob.edit_mode = True
        apply = self.collectConstraintsCheckBox.checkState() == Qt.Unchecked
        use_ccd = self.ccdCheckBox.checkState() == Qt.Checked
        self._animation_editor.translate_joint(joint_name, offset, frame_range, use_ccd, plot, apply)
        joint_knob.edit_mode = False
        self.show_change()

    def slot_clear_constraints(self):
        self._animation_editor.clear_constraints()

    def slot_rotate_joint(self):
        joint_knob = self.get_selected_joint()
        if joint_knob is None:
            return
        joint_name = joint_knob.joint_name
        x = float(self.rotateXLineEdit.text())
        y = float(self.rotateYLineEdit.text())
        z = float(self.rotateZLineEdit.text())
        

        edit_start = self.leftStartFrameSlider.value()
        edit_end = self.leftEndFrameSlider.value()+1
        if edit_start > edit_end:
            print("frame range is wrong", edit_start, edit_end)
            return
        frame_range = edit_start, edit_end
        offset = [x,y,z]
        window_size = int(self.blendRangeLineEdit.text())
        self._animation_editor.rotate_joint(joint_name, offset, frame_range, window_size)
        self.show_change()

    def show_change(self):
        frames = np.array(self.left_controller.get_frames())
        self.original_controller.replace_frames(frames)
        self.original_controller.updateTransformation()

    def slot_smooth_frames(self):
        window_size = int(self.smoothWindowSizeLineEdit.text())       
        if window_size >= 5:
            print("smooth frames using a window size of", window_size)
            self._animation_editor.smooth_using_moving_average(window_size)
        else:
            print("Error: window size must be >= 5")
        
    def slot_concatenate(self):
        options = dict()
        options["activate_smoothing"] = True
        options["window"] = 20
        select_animation_dialog = SelectSceneObjectsDialog(self.scene, get_animation_controllers, self, name="Concatenate", properties=options)
        select_animation_dialog.exec_()
        if select_animation_dialog.success:
            o = self.scene.getObject(select_animation_dialog.selected_node_id)
            options = select_animation_dialog.properties
            animation_controller = o._components["animation_controller"]
            self.left_controller._motion.mv.skeleton = self.left_controller.get_skeleton()
            self._animation_editor.concatenate(animation_controller, options["activate_smoothing"], options["window"])
            self.n_frames = self.left_controller.getNumberOfFrames()
            self.set_frame_range()
            self.show_change()

    def slot_mirror_animation(self):
        self._animation_editor.mirror_animation()
        self.show_change()

    def slot_delete_frames_before(self):
        frame_idx = self._animation_editor.get_current_frame_number()
        self._animation_editor.delete_frames_before(frame_idx)
        

    def slot_delete_frames_after(self):
        frame_idx = self._animation_editor.get_current_frame_number()
        self._animation_editor.delete_frames_after(frame_idx)

    def slot_fix_joint(self):
        joint_knob = self.get_selected_joint()
        if joint_knob is None:
            return
        joint_name = joint_knob.joint_name
        apply = self.collectConstraintsCheckBox.checkState() == Qt.Unchecked
        edit_start = self.leftStartFrameSlider.value()
        edit_end = self.leftEndFrameSlider.value()+1
        joint_knob.edit_mode = True
        frame = self.left_controller.get_current_frame()
        p = self.left_controller.get_joint_position(joint_name, frame)
        p = p.tolist()
        if edit_start < edit_end:
            frame_range = edit_start, edit_end
            self._animation_editor.fix_joint(joint_name, p, frame_range, apply)            
        else:
            print("frame range is wrong", edit_start, edit_end)

        joint_knob.edit_mode = False
        self.show_change()

    def slot_export_command_history(self):
        filename = QFileDialog.getSaveFileName(self, 'Save To File', '.')[0]
        save_json_file(self._animation_editor.command_history, filename)

    def slot_apply_constraints(self, plot=False):
        use_ccd = self.ccdCheckBox.checkState() == Qt.Checked
        if use_ccd:
            self._animation_editor.apply_constraints_using_ccd(plot)
        else:
            self._animation_editor.apply_constraints(plot)

    def slot_resample_motion(self):
        resample_factor = float(self.resampleFactorLineEdit.text())       
        if resample_factor >= 0:
            print("resample frames using a factor of", resample_factor)
            self._animation_editor.resample_motion(resample_factor)
            self.n_frames = self.left_controller.getNumberOfFrames()
            self.set_frame_range()
            self.show_change()
        else:
            print("Error: resample factor must be > 0", resample_factor)

    def slot_set_fps(self):
        fps = float(self.fpsLineEdit.text())       
        if fps >= 0:
            print("set fps to", fps)
            self.left_controller._motion.mv.frame_time =  1.0/fps
            self.show_change()
        else:
            print("Error: window size must be > 0", fps)
    
    def flip_blender_coordinate_systems(self):
        self._animation_editor.flip_blender_coordinate_systems()

    def guess_ground_height(self):
        source_ground_height = self._animation_editor.guess_ground_height(False)
        self.sourceGroundHeightLineEdit.setText(str(source_ground_height))

    def move_to_ground(self):
        source_ground_height = float(self.sourceGroundHeightLineEdit.text())
        target_ground_height = float(self.targetGroundHeightLineEdit.text())
        self._animation_editor.move_to_ground(source_ground_height, target_ground_height)