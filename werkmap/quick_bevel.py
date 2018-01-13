import bpy
import bgl

from math import sqrt, pi, cos, sin
# Addon info

bl_info = {
    'name': 'Quick Undestructive Bevel',
    'author': 'Bert Van den Bosch',
    'version': (1, 0, 0),
    'blender': (2, 7, 9),
    'location': '3D View > SpacebarMenu > Quick Bevel',
    'description': 'Model with undestructe bevel modifiers and vertex maps',
    'category': 'Mesh'}

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
            if event.type in {'PAGE_UP', 'NUMPAD_PLUS'}:
                if event.value == 'RELEASE':
                    self.segments += 1
            else:
                self.segments += 1
            self.execute(context)

        if event.type in {'WHEELDOWNMOUSE', 'PAGE_DOWN', 'NUMPAD_MINUS'}:
            if self.segments > 0:
                if event.type in {'PAGE_DOWN', 'NUMPAD_MINUS'}:
                    if event.value == 'RELEASE':
                        self.segments -= 1
                else:
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

        # No vertex group when in object mode
        if self.obj.mode == 'OBJECT':
            curBevel = 'Bevel_main'

            self.curMod = [mod for mod in self.obj.modifiers if mod.name == curBevel]
            if len(self.curMod) != 0:
                self.curMod = self.curMod[0]

                # Do not reset amount of segments
                self.segments = self.curMod.segments

            else:
                # Create the modifier
                new_mod = self.obj.modifiers.new(curBevel, 'BEVEL')
                new_mod.use_clamp_overlap = False
                new_mod.show_expanded = False

                self.curMod = new_mod

            return

        curBevel = 'Bevel_' + str(self.obj.bevel_settings.index)

        # Create the vertex group
        new_group = self.obj.vertex_groups.new(curBevel)

        bpy.ops.object.mode_set(mode='OBJECT')
        self.obj.update_from_editmode()

        # Create the vertex group
        verts = [v.index for v in self.obj.data.vertices if v.select]

        new_group.add(verts, 1, 'REPLACE')

        bpy.ops.object.mode_set(mode='EDIT')

        # Create the modifier
        new_mod = self.obj.modifiers.new(curBevel, 'BEVEL')
        # Modifier settings:
        new_mod.limit_method = 'VGROUP'
        new_mod.vertex_group = curBevel
        new_mod.use_clamp_overlap = False
        new_mod.show_expanded = False

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

def unregister():
    bpy.utils.unregister_class(QuickBevel)
    bpy.utils.unregister_class(ObjectProps)