import bpy
import bgl
import blf
from math import pi, cos, sin

def draw_circle(self, context, rad, res):
    bgl.glPushAttrib(bgl.GL_ENABLE_BIT)

    bgl.glEnable(bgl.GL_BLEND)

    bgl.glBegin(bgl.GL_LINE_LOOP)

    i = 0
    while i < 2*pi:
        bgl.glVertex2f( self.mousex0 + rad * cos(i), self.mousey0 + rad * sin(i))

        i += pi * 2/res

    bgl.glEnd()
    bgl.glPopAttrib()

    bgl.glDisable(bgl.GL_BLEND)

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

                self.add_handlers(context)

            if event.value == 'RELEASE':
                self.remove_handlers()
                return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            self.remove_handlers()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.mousex0 = None
        self.mousey0 = None

        self.mousex = None
        self.mousey = None

        if context.area.type == 'VIEW_3D':
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

    def add_handlers(self, context):
        args = (self, context)

        self._handle0 = bpy.types.SpaceView3D.draw_handler_add(draw_line, args, 'WINDOW', 'POST_PIXEL')

        args = (self, context, 8, 9)
        self._handle1 = bpy.types.SpaceView3D.draw_handler_add(draw_circle, args, 'WINDOW', 'POST_PIXEL')

    def remove_handlers(self):
        bpy.types.SpaceView3D.draw_handler_remove(self._handle0, 'WINDOW')

        bpy.types.SpaceView3D.draw_handler_remove(self._handle1, 'WINDOW')


def register():
    bpy.utils.register_class(ModalDrawOperator)


def unregister():
    bpy.utils.unregister_class(ModalDrawOperator)


if __name__ == "__main__":
    register()
