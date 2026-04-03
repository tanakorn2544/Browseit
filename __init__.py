# SPDX-License-Identifier: GPL-3.0-or-later

bl_info = {
    "name": "BrowseIt",
    "author": "User",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "3D Viewport > Alt+Q (Pie) | Alt+Shift+Q (Search)",
    "description": "Pie menu to quickly jump to favorite N-Panel addon tabs, plus search.",
    "category": "Interface",
}

import bpy
from bpy.types import AddonPreferences, Menu, Operator
from bpy.props import StringProperty, EnumProperty


# ── Helpers ─────────────────────────────────────────────────────────────────

def get_npanel_categories():
    """Collect all unique bl_category values from VIEW_3D / UI panels."""
    cats = set()
    seen = set()

    def _walk(cls):
        cid = id(cls)
        if cid in seen:
            return
        seen.add(cid)
        try:
            if (
                getattr(cls, "bl_space_type", "") == "VIEW_3D"
                and getattr(cls, "bl_region_type", "") == "UI"
                and hasattr(cls, "bl_category")
                and cls.bl_category
            ):
                cats.add(cls.bl_category)
        except Exception:
            pass
        for sub in cls.__subclasses__():
            _walk(sub)

    _walk(bpy.types.Panel)
    return sorted(cats)


def enum_npanel_tabs(self, context):
    """Dynamic enum callback listing all N-panel tab categories."""
    items = [("NONE", "— Empty —", "No addon assigned", 'BLANK1', 0)]
    for i, cat in enumerate(get_npanel_categories(), start=1):
        items.append((cat, cat, f"Switch to '{cat}' tab", 'PREFERENCES', i))
    return items


def get_prefs():
    name = __package__ or __name__
    return bpy.context.preferences.addons[name].preferences


# ── Operator: switch to a tab ───────────────────────────────────────────────

class BROWSEIT_OT_goto_tab(Operator):
    bl_idname = "browseit.goto_tab"
    bl_label = "Go to N-Panel Tab"
    bl_description = "Open the sidebar and switch to a specific tab"
    bl_options = {'INTERNAL'}

    tab_name: StringProperty(default="")  # type: ignore

    def execute(self, context):
        tab = self.tab_name
        if not tab or tab == "NONE":
            self.report({'WARNING'}, "No tab assigned to this slot.")
            return {'CANCELLED'}

        # Find the 3D Viewport area
        area = context.area if context.area and context.area.type == 'VIEW_3D' else None
        if area is None:
            for a in context.screen.areas:
                if a.type == 'VIEW_3D':
                    area = a
                    break
        if area is None:
            self.report({'WARNING'}, "No 3D Viewport found.")
            return {'CANCELLED'}

        # Ensure sidebar is visible
        space = area.spaces.active
        if hasattr(space, "show_region_ui"):
            space.show_region_ui = True

        # Switch the active tab
        for region in area.regions:
            if region.type == 'UI':
                region.active_panel_category = tab
                break

        area.tag_redraw()
        self.report({'INFO'}, f"Switched to '{tab}'")
        return {'FINISHED'}


# ── Operator: search tabs ──────────────────────────────────────────────────

class BROWSEIT_OT_search_tab(Operator):
    bl_idname = "browseit.search_tab"
    bl_label = "Search N-Panel Tab"
    bl_description = "Search for any N-Panel tab by name"
    bl_options = {'INTERNAL'}
    bl_property = "tab_result"

    tab_result: EnumProperty(name="Tab", items=enum_npanel_tabs)  # type: ignore

    def execute(self, context):
        if self.tab_result and self.tab_result != "NONE":
            bpy.ops.browseit.goto_tab(tab_name=self.tab_result)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'CANCELLED'}


# ── Pie Menu ───────────────────────────────────────────────────────────────

NUM_SLOTS = 8

class BROWSEIT_MT_pie(Menu):
    bl_idname = "BROWSEIT_MT_pie"
    bl_label = "BrowseIt"

    def draw(self, context):
        pie = self.layout.menu_pie()
        prefs = get_prefs()

        # Pie order: W, E, S, N, NW, NE, SW, SE
        for i in range(1, NUM_SLOTS + 1):
            tab = prefs.get_slot(i)
            if tab and tab != "NONE":
                op = pie.operator(
                    "browseit.goto_tab",
                    text=tab,
                    icon='RIGHTARROW_THIN',
                )
                op.tab_name = tab
            else:
                # Empty slot — show a placeholder
                pie.operator(
                    "browseit.goto_tab",
                    text=f"Slot {i} (empty)",
                    icon='BLANK1',
                ).tab_name = "NONE"


# ── A secondary pie/popup that includes Search ─────────────────────────────

class BROWSEIT_MT_header(Menu):
    """Extra menu shown from the pie — contains the Search button."""
    bl_idname = "BROWSEIT_MT_header"
    bl_label = "BrowseIt Extra"

    def draw(self, context):
        layout = self.layout
        layout.operator("browseit.search_tab", text="Search Tabs…", icon='VIEWZOOM')


# ── Preferences ────────────────────────────────────────────────────────────

class BrowseItPreferences(AddonPreferences):
    bl_idname = __package__ or __name__

    slot_1: EnumProperty(name="Slot 1 (West)",      items=enum_npanel_tabs)  # type: ignore
    slot_2: EnumProperty(name="Slot 2 (East)",      items=enum_npanel_tabs)  # type: ignore
    slot_3: EnumProperty(name="Slot 3 (South)",     items=enum_npanel_tabs)  # type: ignore
    slot_4: EnumProperty(name="Slot 4 (North)",     items=enum_npanel_tabs)  # type: ignore
    slot_5: EnumProperty(name="Slot 5 (NW)",        items=enum_npanel_tabs)  # type: ignore
    slot_6: EnumProperty(name="Slot 6 (NE)",        items=enum_npanel_tabs)  # type: ignore
    slot_7: EnumProperty(name="Slot 7 (SW)",        items=enum_npanel_tabs)  # type: ignore
    slot_8: EnumProperty(name="Slot 8 (SE)",        items=enum_npanel_tabs)  # type: ignore

    def get_slot(self, index: int) -> str:
        return getattr(self, f"slot_{index}", "NONE")

    def draw(self, context):
        layout = self.layout
        layout.label(text="Assign N-Panel tabs to pie menu slots:", icon='MENU_PANEL')

        box = layout.box()
        grid = box.column(align=True)
        for i in range(1, NUM_SLOTS + 1):
            row = grid.row(align=True)
            row.label(text=f"Slot {i}:")
            row.prop(self, f"slot_{i}", text="")

        layout.separator()
        layout.label(text="Hotkeys:", icon='EVENT_OS')
        col = layout.column(align=True)
        col.label(text="  Alt + Q  →  Open Favorites Pie Menu")
        col.label(text="  Alt + Shift + Q  →  Search All Tabs")


# ── Registration ───────────────────────────────────────────────────────────

classes = (
    BrowseItPreferences,
    BROWSEIT_OT_goto_tab,
    BROWSEIT_OT_search_tab,
    BROWSEIT_MT_pie,
    BROWSEIT_MT_header,
)

addon_keymaps = []


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type='VIEW_3D')

        # Alt+Q → pie menu
        kmi = km.keymap_items.new(
            "wm.call_menu_pie",
            type='Q', value='PRESS', alt=True,
        )
        kmi.properties.name = "BROWSEIT_MT_pie"
        addon_keymaps.append((km, kmi))

        # Alt+Shift+Q → search popup
        kmi = km.keymap_items.new(
            "browseit.search_tab",
            type='Q', value='PRESS', alt=True, shift=True,
        )
        addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
