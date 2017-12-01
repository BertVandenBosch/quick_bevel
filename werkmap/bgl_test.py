import bpy
import bgl
import blf


def draw_line(self, context):
    
    bgl.glPushAttrib(bgl.GL_ENABLE_BIT)
    
    bgl.glEnable(bgl.GL_BLEND)

    # style
    bgl.glLineWidth(3)
    bgl.glColor4f(1.0, 1.0, 1.0, 0.4)
    bgl.glLineStipple(3, 0xAAAA)
    bgl.glEnable(bgl.GL_LINE_STIPPLE)

    bgl.glBegin(bgl.GL_LINES)

    bgl.glVertex2i(self.mousex0, self.mousey0)
    bgl.glVertex2i(self.mousex, self.mousey)

    bgl.glEnd()
    bgl.glPopAttrib()

    bgl.glDisable(bgl.GL_BLEND)

    # reset style
    bgl.glLineWidth(1)
    bgl.glColor4f(1.0, 1.0, 1.0, 10)

class ModalDrawOperator(bpy.types.Operator):
    """Draw a line with the mouse"""
    bl_idname = "view3d.modal_operator"
    bl_label = "Simple Modal View3D Operator"

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'MOUSEMOVE':
            self.mousex = event.mouse_region_x
            self.mousey = event.mouse_region_y

        elif event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                self.mousex0 = event.mouse_region_x
                self.mousey0 = event.mouse_region_y

                self.mousex = self.mousex0
                self.mousey = self.mousey0

                args = (self, context)
                self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_line, args, 'WINDOW', 'POST_PIXEL')

            if event.value == 'RELEASE':
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
                return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.mousex0 = None
        self.mousey0 = None

        self.mousex = None
        self.mousey = None

        if context.area.type == 'VIEW_3D':
            # the arguments we pass the the callback
            # args = (self, context)
            # Add the region OpenGL drawing callback
            # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
            # self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_line, args, 'WINDOW', 'POST_PIXEL')

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


def register():
    bpy.utils.register_class(ModalDrawOperator)


def unregister():
    bpy.utils.unregister_class(ModalDrawOperator)


if __name__ == "__main__":
    register()
