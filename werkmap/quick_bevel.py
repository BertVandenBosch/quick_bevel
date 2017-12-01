import bpy
import bgl

from math import sqrt, pi, cos, sin


# TODO:
# bgl stuff: text
# add extra segments
# add short-cut keybindings
# to addon-form
# improve undo

class ObjectProps(bpy.types.PropertyGroup):
    index = bpy.props.IntProperty(default=0)


def draw_circle(self, context, rad, res):
    bgl.glPushAttrib(bgl.GL_ENABLE_BIT)

    bgl.glEnable(bgl.GL_BLEND)

    bgl.glBegin(bgl.GL_LINE_LOOP)

    i = 0
    while i < 2 * pi:
        bgl.glVertex2f(self.gl_mousex0 + rad * cos(i), self.gl_mousey0 + rad * sin(i))

        i += pi * 2 / res

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

    bgl.glVertex2i(self.gl_mousex0, self.gl_mousey0)
    bgl.glVertex2i(self.gl_mousex, self.gl_mousey)

    bgl.glEnd()
    bgl.glPopAttrib()

    bgl.glDisable(bgl.GL_BLEND)

    # reset style
    bgl.glLineWidth(1)
    bgl.glColor4f(1.0, 1.0, 1.0, 10)

class QuickBevel(bpy.types.Operator):
    bl_label = "Quick Undestructive Bevel"
    bl_idname = "object.quick_bevel"
    bl_options = {'UNDO'}

    # TODO: Add classmethod poll --> object selected or in Edit Mode?

    def invoke(self, context, event):
        self.obj = bpy.context.active_object

        self.mousex0 = None
        self.mousey0 = None

        self.curMod = None
        self.dist = None
        self.segments = 1

        # GL variables

        self.gl_mousex0 = None
        self.gl_mousey0 = None

        self.gl_mousex = None
        self.gl_mousey = None

        if context.area.type == 'VIEW_3D':
            context.window_manager.modal_handler_add(self)

        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'MOUSEMOVE':
            if None not in {self.mousex0, self.mousey0}:
                self.dist = sqrt((event.mouse_x - self.mousex0) ** 2 + (event.mouse_y - self.mousey0) ** 2) / 100

                self.execute(context)

            self.gl_mousex = event.mouse_region_x
            self.gl_mousey = event.mouse_region_y

            return {'RUNNING_MODAL'}

        if event.type == 'LEFTMOUSE':
            # Mouse down
            if event.value == 'PRESS':
                self.mousex0 = event.mouse_x
                self.mousey0 = event.mouse_y

                self.dist = 0

                self.gl_mousex0 = event.mouse_region_x
                self.gl_mousey0 = event.mouse_region_y

                self.setUp()
                self.add_handlers(context)
                self.execute(context)

            if event.value == 'RELEASE':
                self.remove_handlers()
                return {'FINISHED'}

        if event.type in {'WHEELUPMOUSE', 'PAGE_UP', 'NUMPAD_PLUS'}:
            self.segments += 1
            self.execute(context)

        if event.type in {'WHEELDOWNMOUSE', 'PAGE_DOWN', 'NUMPAD_MINUS'}:
            if self.segments > 0:
                self.segments -= 1
                self.execute(context)

        if event.type == 'MIDDLEMOUSE':
            return {'PASS_TROUGH'}

        if event.type in {'ESC', 'RIGHTMOUSE'}:
            self.remove_handlers()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def execute(self, context):
        if self.curMod is not None:
            self.curMod.width = self.dist
            self.curMod.segments = self.segments
        return {'FINISHED'}

    ###### Custom methods ######

    def setUp(self):

        # Attach the object settings to the active object
        if not hasattr(self.obj, 'bevel_settings'):
            bpy.types.Object.bevel_settings = bpy.props.PointerProperty(type=ObjectProps)
            self.obj.bevel_settings.index = 0

        curBevel = 'Bevel_' + str(self.obj.bevel_settings.index)

        # Create the vertex group
        new_group = self.obj.vertex_groups.new(curBevel)

        bpy.ops.object.mode_set(mode='OBJECT')
        self.obj.update_from_editmode()

        verts = [v.index for v in self.obj.data.vertices if v.select]

        new_group.add(verts, 1, 'REPLACE')

        bpy.ops.object.mode_set(mode='EDIT')

        # Create the modifier
        new_mod = self.obj.modifiers.new(curBevel, 'BEVEL')
        # Modifier settings:
        new_mod.limit_method = 'VGROUP'
        new_mod.vertex_group = curBevel
        # new_mod.offset_type = 'PERCENT'
        new_mod.use_clamp_overlap = False

        self.curMod = new_mod

        self.obj.bevel_settings.index += 1

    # GL methods
    def add_handlers(self, context):
        args = (self, context)

        self._handle0 = bpy.types.SpaceView3D.draw_handler_add(draw_line, args, 'WINDOW', 'POST_PIXEL')

        args = (self, context, 8, 9)
        self._handle1 = bpy.types.SpaceView3D.draw_handler_add(draw_circle, args, 'WINDOW', 'POST_PIXEL')

    def remove_handlers(self):
        bpy.types.SpaceView3D.draw_handler_remove(self._handle0, 'WINDOW')

        bpy.types.SpaceView3D.draw_handler_remove(self._handle1, 'WINDOW')


def register():
    bpy.utils.register_class(QuickBevel)
    bpy.utils.register_class(ObjectProps)


# Run the register module when this file gets called from itself
if __name__ == '__main__':
    register()
