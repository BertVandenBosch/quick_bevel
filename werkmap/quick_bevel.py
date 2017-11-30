import bpy
import bgl
import blf
import math


# TODO:
# bgl stuff: mousestarting point + dotted line?
# add short-cut keybindings
# to addon-form
# improve undo

class ObjectProps(bpy.types.PropertyGroup):
    index = bpy.props.IntProperty(default=0)


class QuickBevel(bpy.types.Operator):
    bl_label = "Quick Undestructive Bevel"
    bl_idname = "object.quick_bevel"
    bl_options = {'UNDO'}

    # TODO: Add classmethod poll --> object selected or in Edit Mode?

    def invoke(self, context, event):
        self.obj = bpy.context.active_object

        self.mousex0 = None
        self.mousey0 = None

        self.dist = None

        self.curMod = None

        # self.setUp()

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):

        if event.type == 'MOUSEMOVE':
            if None not in {self.mousex0, self.mousey0}:
                self.dist = math.sqrt((event.mouse_x - self.mousex0) ** 2 + (event.mouse_y - self.mousey0) ** 2) / 100

                self.execute(context)

            return {'RUNNING_MODAL'}

        if event.type == 'LEFTMOUSE':
            # Mouse down
            if event.value == 'PRESS':
                self.mousex0 = event.mouse_x
                self.mousey0 = event.mouse_y

                self.dist = 0

                self.setUp()
                self.execute(context)

            if event.value == 'RELEASE':
                return {'FINISHED'}

        if event.type in {'ESC', 'RIGHTMOUSE'}:
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def execute(self, context):
        if self.curMod is not None:
            self.curMod.width = self.dist
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


def register():
    bpy.utils.register_class(QuickBevel)
    bpy.utils.register_class(ObjectProps)


# Run the register module when this file gets called from itself
if __name__ == '__main__':
    register()
