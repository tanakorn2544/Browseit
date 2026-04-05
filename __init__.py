# SPDX-License-Identifier: GPL-3.0-or-later

bl_info = {
    "name": "BrowseIt",
    "author": "Korn Sensei",
    "version": (1, 0, 2),
    "blender": (4, 0, 0),
    "location": "3D Viewport > Alt+Q (Pie) | Alt+Shift+Q (Search)",
    "description": "Pie menu to quickly jump to favorite N-Panel addon tabs, plus search.",
    "category": "Interface",
}

import bpy
from bpy.types import AddonPreferences, Menu, Operator
from bpy.props import StringProperty, EnumProperty, IntProperty


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


ADDON_NAME = __package__ or __name__

def get_prefs():
    try:
        return bpy.context.preferences.addons[ADDON_NAME].preferences
    except KeyError:
        return None


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


# ── Operator: search & add to pie (right-click / Alt+Ctrl+Q) ──────────────

class BROWSEIT_OT_search_add_to_pie(Operator):
    bl_idname = "browseit.search_add_to_pie"
    bl_label = "Search & Add to Pie"
    bl_description = "Search for a tab and assign it to a pie menu slot"
    bl_options = {'INTERNAL'}
    bl_property = "tab_result"

    tab_result: EnumProperty(name="Tab", items=enum_npanel_tabs)  # type: ignore

    def execute(self, context):
        if self.tab_result and self.tab_result != "NONE":
            bpy.ops.browseit.pick_slot('INVOKE_DEFAULT', tab_name=self.tab_result)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'CANCELLED'}


# ── Operator: pie slot action (navigate or reassign) ──────────────────────

class BROWSEIT_OT_pie_slot_action(Operator):
    """Click to navigate · Ctrl+Click to reassign · Click empty slot to assign"""
    bl_idname = "browseit.pie_slot_action"
    bl_label = "Pie Slot Action"
    bl_description = "Navigate to tab, or Ctrl+Click to reassign this slot"
    bl_options = {'INTERNAL'}

    slot_index: IntProperty(default=0)  # type: ignore
    tab_name: StringProperty(default="")  # type: ignore

    def invoke(self, context, event):
        tab = self.tab_name
        is_empty = (not tab or tab == "NONE")

        # Ctrl+Click or empty slot → open search to reassign
        if event.ctrl or is_empty:
            bpy.ops.browseit.reassign_slot(
                'INVOKE_DEFAULT', slot_index=self.slot_index,
            )
            return {'FINISHED'}

        # Normal click → navigate to the tab
        bpy.ops.browseit.goto_tab(tab_name=tab)
        return {'FINISHED'}


# ── Operator: reassign a specific pie slot via search ─────────────────────

class BROWSEIT_OT_reassign_slot(Operator):
    """Search for a tab and assign it directly to a specific pie slot."""
    bl_idname = "browseit.reassign_slot"
    bl_label = "Reassign Pie Slot"
    bl_description = "Search for a tab and assign it to this pie slot"
    bl_options = {'INTERNAL'}
    bl_property = "tab_result"

    slot_index: IntProperty(default=0)  # type: ignore
    tab_result: EnumProperty(name="Tab", items=enum_npanel_tabs)  # type: ignore

    def execute(self, context):
        prefs = get_prefs()
        if prefs is None:
            self.report({'ERROR'}, "Addon preferences not found.")
            return {'CANCELLED'}

        if self.tab_result and self.tab_result != "NONE":
            setattr(prefs, f"slot_{self.slot_index}", self.tab_result)
            _labels = ["West", "East", "South", "North", "NW", "NE", "SW", "SE"]
            label = _labels[self.slot_index - 1] if 1 <= self.slot_index <= 8 else "?"
            self.report({'INFO'}, f"Slot {self.slot_index} ({label}) → '{self.tab_result}'")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'CANCELLED'}


# ── Operator: assign tab to pie slot ───────────────────────────────────────

class BROWSEIT_OT_pick_slot(Operator):
    bl_idname = "browseit.pick_slot"
    bl_label = "Add to Pie Menu"
    bl_description = "Assign the selected tab to a pie menu slot"
    bl_options = {'INTERNAL'}

    tab_name: StringProperty(name="Tab", default="")  # type: ignore

    slot: EnumProperty(
        name="Slot",
        items=[
            ('1', "Slot 1 — West",  ""),
            ('2', "Slot 2 — East",  ""),
            ('3', "Slot 3 — South", ""),
            ('4', "Slot 4 — North", ""),
            ('5', "Slot 5 — NW",    ""),
            ('6', "Slot 6 — NE",    ""),
            ('7', "Slot 7 — SW",    ""),
            ('8', "Slot 8 — SE",    ""),
        ],
    )  # type: ignore

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=260)

    def draw(self, context):
        layout = self.layout
        layout.label(text=f"Add '{self.tab_name}' to pie menu?", icon='SOLO_ON')
        layout.separator(factor=0.4)
        layout.prop(self, "slot")

        # Show current slot assignments for reference
        layout.separator(factor=0.8)
        layout.label(text="Current Assignments:", icon='MENU_PANEL')
        prefs = get_prefs()
        if prefs:
            _labels = ["West", "East", "South", "North", "NW", "NE", "SW", "SE"]
            box = layout.box()
            col = box.column(align=True)
            for i in range(1, NUM_SLOTS + 1):
                current = prefs.get_slot(i)
                lbl = _labels[i - 1]
                if current and current != "NONE":
                    col.label(text=f"Slot {i} ({lbl}):  {current}", icon='RIGHTARROW_THIN')
                else:
                    col.label(text=f"Slot {i} ({lbl}):  — empty —", icon='BLANK1')

    def execute(self, context):
        prefs = get_prefs()
        if prefs is None:
            self.report({'ERROR'}, "Addon preferences not found. Install the addon properly.")
            return {'CANCELLED'}
        setattr(prefs, f"slot_{self.slot}", self.tab_name)
        self.report({'INFO'}, f"'{self.tab_name}' → Slot {self.slot}")
        return {'FINISHED'}


# ── Pie Menu ───────────────────────────────────────────────────────────────

NUM_SLOTS = 8

class BROWSEIT_MT_pie(Menu):
    bl_idname = "BROWSEIT_MT_pie"
    bl_label = "BrowseIt"

    def draw(self, context):
        pie = self.layout.menu_pie()
        prefs = get_prefs()
        if prefs is None:
            pie.label(text="Addon not installed properly")
            return

        # Pie order: W, E, S, N, NW, NE, SW, SE
        # Click → navigate  |  Ctrl+Click → reassign  |  Empty → assign
        for i in range(1, NUM_SLOTS + 1):
            tab = prefs.get_slot(i)
            if tab and tab != "NONE":
                op = pie.operator(
                    "browseit.pie_slot_action",
                    text=tab,
                    icon='RIGHTARROW_THIN',
                )
                op.tab_name = tab
                op.slot_index = i
            else:
                op = pie.operator(
                    "browseit.pie_slot_action",
                    text=f"Slot {i} (empty)",
                    icon='ADD',
                )
                op.tab_name = "NONE"
                op.slot_index = i


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
        col.label(text="  Alt + Ctrl + Q  →  Search & Add to Pie")
        col.label(text="  Ctrl + Click (pie)  →  Reassign Slot")


# ── Registration ───────────────────────────────────────────────────────────

classes = (
    BrowseItPreferences,
    BROWSEIT_OT_goto_tab,
    BROWSEIT_OT_pie_slot_action,
    BROWSEIT_OT_reassign_slot,
    BROWSEIT_OT_pick_slot,
    BROWSEIT_OT_search_tab,
    BROWSEIT_OT_search_add_to_pie,
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

        # Alt+Shift+Q → search & navigate
        kmi = km.keymap_items.new(
            "browseit.search_tab",
            type='Q', value='PRESS', alt=True, shift=True,
        )
        addon_keymaps.append((km, kmi))

        # Alt+Ctrl+Q → search & add to pie
        kmi = km.keymap_items.new(
            "browseit.search_add_to_pie",
            type='Q', value='PRESS', alt=True, ctrl=True,
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
