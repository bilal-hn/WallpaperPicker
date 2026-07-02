#!/usr/bin/env python3
import gi
import os
import sys
import fcntl
import threading
import subprocess
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib

WALLPAPER_DIR = os.path.expanduser("~/Pictures/Wallpapers")
SUPPORTED = (".jpg", ".jpeg", ".png", ".webp")

THUMB_W = 260
THUMB_H = 146
STRIP_HEIGHT = 220        
TOP_MARGIN = 60           

# --- SINGLE INSTANCE LOCK ---
LOCK_FILE = os.path.join(os.path.expanduser("~"), ".wallpaper_picker.lock")
try:
    lock_fd = open(LOCK_FILE, "w")
    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except IOError:
    sys.exit(0)


class WallpaperPicker(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.moiz.wallpaperpicker")
        self.connect("activate", self.on_activate)
        self.active_child = None  
        self.original_wallpaper = None  
        self.confirmed = False  
        
        # Performance Image Cache System
        self.pixbuf_cache = {}
        
        # Crossfade Preview System Variables
        self.current_preview_pixbuf = None
        self.next_preview_pixbuf = None
        self.preview_alpha = 1.0
        self.fade_transition_id = 0

    def on_activate(self, app):
        self.window = Gtk.ApplicationWindow(application=self)
        self.window.set_title("Wallpaper Picker")
        self.window.set_decorated(False)
        self.window.set_resizable(False)

        geo = self.get_monitor_geometry()
        self.monitor_geo = geo
        self.window.set_default_size(geo.width, STRIP_HEIGHT)

        self.main_overlay = Gtk.Overlay()
        
        self.bg_drawing_area = Gtk.DrawingArea()
        self.bg_drawing_area.set_draw_func(self.draw_bg_preview_canvas)
        self.main_overlay.set_child(self.bg_drawing_area)
        
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        outer.add_css_class("dock")

        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        self.scrolled.set_vexpand(True)

        self.flow = Gtk.FlowBox()
        self.flow.set_orientation(Gtk.Orientation.VERTICAL)
        self.flow.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flow.set_min_children_per_line(1)
        self.flow.set_max_children_per_line(1)
        self.flow.set_row_spacing(0)
        self.flow.set_column_spacing(18)
        self.flow.set_margin_top(20)
        self.flow.set_margin_bottom(20)
        self.flow.set_margin_start(24)
        self.flow.set_margin_end(24)

        self.scrolled.set_child(self.flow)
        outer.append(self.scrolled)
        
        self.main_overlay.add_overlay(outer)
        self.window.set_child(self.main_overlay)

        self.original_wallpaper = self.get_current_wallpaper()
        
        if self.original_wallpaper and os.path.exists(self.original_wallpaper):
            threading.Thread(
                target=self.load_image_async, 
                args=(self.original_wallpaper, geo.width, geo.height, "initial"),
                daemon=True
            ).start()

        self.load_wallpapers()

        provider = Gtk.CssProvider()
        provider.load_from_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.css"))
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        controller = Gtk.EventControllerKey()
        controller.connect("key-pressed", self.key_pressed)
        self.window.add_controller(controller)

        self.window.connect("close-request", self.on_close_request)

        self.window.set_opacity(0)
        self.window.present()
        
        GLib.idle_add(self.position_window)

    def get_monitor_geometry(self):
        display = Gdk.Display.get_default()
        monitors = display.get_monitors()
        monitor = monitors.get_item(0)
        return monitor.get_geometry()

    def get_current_wallpaper(self):
        try:
            res = subprocess.run(
                "gsettings get org.cinnamon.desktop.background picture-uri",
                shell=True, capture_output=True, text=True, check=True
            )
            uri = res.stdout.strip().strip("'")
            if uri.startswith("file://"):
                return uri[7:]
        except Exception:
            pass
        return None

    def position_window(self):
        geo = self.monitor_geo
        x = geo.x
        y = geo.y + TOP_MARGIN
        title = "Wallpaper Picker"

        try:
            subprocess.run(f"wmctrl -r '{title}' -e '0,{x},{y},{geo.width},{STRIP_HEIGHT}'", shell=True, check=False)
            subprocess.run(f"wmctrl -r '{title}' -b add,above", shell=True, check=False)
            subprocess.run(f"wmctrl -a '{title}'", shell=True, check=False)
        except Exception as e:
            print("Window positioning fault:", e)

        self.window.set_opacity(1)
        self.window.grab_focus()
        GLib.timeout_add(50, self.focus_active_child)
        return False

    def focus_active_child(self):
        if self.active_child is not None:
            self.active_child.grab_focus()
        else:
            first = self.flow.get_child_at_index(0)
            if first is not None:
                first.grab_focus()
        return False

    def load_wallpapers(self):
        if not os.path.exists(WALLPAPER_DIR):
            return

        current_path = self.original_wallpaper
        files = sorted(os.listdir(WALLPAPER_DIR))
        paths = [os.path.join(WALLPAPER_DIR, f) for f in files if f.lower().endswith(SUPPORTED)]
        
        if not paths:
            return

        if current_path in paths:
            paths.remove(current_path)
            paths.insert(0, current_path)

        for path in paths:
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, THUMB_W, THUMB_H, True)
            except Exception:
                continue

            picture = Gtk.Picture.new_for_pixbuf(pixbuf)
            picture.set_can_shrink(False)
            picture.set_content_fit(Gtk.ContentFit.COVER)

            overlay = Gtk.Overlay()
            overlay.set_size_request(THUMB_W, THUMB_H)
            overlay.set_child(picture)

            button = Gtk.Button()
            button.set_has_frame(False)
            button.set_child(overlay)
            button.add_css_class("wallpaper")
            button.set_focusable(False) 
            button.connect("clicked", self.change_wallpaper, path)

            self.flow.insert(button, -1)
            GLib.idle_add(self.setup_child_events, button, path, path == current_path)

    def setup_child_events(self, button, path, is_active):
        child = button.get_parent()
        if not child:
            return False
            
        child.set_focusable(True)
        
        focus_controller = Gtk.EventControllerFocus()
        focus_controller.connect("enter", lambda *_: self.start_crossfade_preview(path))
        child.add_controller(focus_controller)

        motion_controller = Gtk.EventControllerMotion()
        motion_controller.connect("enter", lambda *_: self.start_crossfade_preview(path))
        child.add_controller(motion_controller)

        if is_active:
            child.add_css_class("selected")
            self.active_child = child
            
        return False

    def load_image_async(self, path, width, height, target_type):
        try:
            if path in self.pixbuf_cache:
                pixbuf = self.pixbuf_cache[path]
            else:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, width, height, False)
                self.pixbuf_cache[path] = pixbuf
            
            if target_type == "initial":
                GLib.idle_add(self.set_initial_bg, pixbuf)
            elif target_type == "hover":
                GLib.idle_add(self.trigger_fade, pixbuf, path)
        except Exception:
            pass

    def set_initial_bg(self, pixbuf):
        self.current_preview_pixbuf = pixbuf
        self.bg_drawing_area.queue_draw()
        return False

    def start_crossfade_preview(self, path):
        if not os.path.exists(path):
            return

        if self.fade_transition_id > 0:
            GLib.source_remove(self.fade_transition_id)
            self.fade_transition_id = 0

        if self.next_preview_pixbuf and self.preview_alpha < 1.0:
            self.current_preview_pixbuf = self.next_preview_pixbuf

        geo = self.monitor_geo
        
        threading.Thread(
            target=self.load_image_async, 
            args=(path, geo.width, geo.height, "hover"),
            daemon=True
        ).start()

    def trigger_fade(self, pixbuf, path):
        self.next_preview_pixbuf = pixbuf
        self.preview_alpha = 0.0
        self.fade_transition_id = GLib.timeout_add(16, self.update_crossfade_step, path)
        return False

    def update_crossfade_step(self, target_path):
        self.preview_alpha += 0.12
        if self.preview_alpha >= 1.0:
            self.preview_alpha = 1.0
            self.current_preview_pixbuf = self.next_preview_pixbuf
            self.next_preview_pixbuf = None
            self.bg_drawing_area.queue_draw()
            
            escaped_path = target_path.replace("'", "'\\''")
            subprocess.run(
                f"gsettings set org.cinnamon.desktop.background picture-uri 'file://{escaped_path}'",
                shell=True, check=False
            )
            self.fade_transition_id = 0
            return False

        self.bg_drawing_area.queue_draw()
        return True

    def draw_bg_preview_canvas(self, drawing_area, cr, width, height, user_data=None):
        if self.current_preview_pixbuf:
            Gdk.cairo_set_source_pixbuf(cr, self.current_preview_pixbuf, 0, 0)
            cr.paint()

        if self.next_preview_pixbuf and self.preview_alpha < 1.0:
            Gdk.cairo_set_source_pixbuf(cr, self.next_preview_pixbuf, 0, 0)
            cr.paint_with_alpha(self.preview_alpha)

    def change_wallpaper(self, button, path):
        """Instantly commits selection to the desktop environment and exits."""
        if self.fade_transition_id > 0:
            GLib.source_remove(self.fade_transition_id)
            self.fade_transition_id = 0
            
        self.confirmed = True
        self.final_exit(path)

    def final_exit(self, path):
        escaped_path = path.replace("'", "'\\''")
        subprocess.run(
            f"gsettings set org.cinnamon.desktop.background picture-uri 'file://{escaped_path}'",
            shell=True, check=False
        )
        self.quit()

    def on_close_request(self, window):
        if self.fade_transition_id > 0:
            GLib.source_remove(self.fade_transition_id)
        if not self.confirmed and self.original_wallpaper:
            escaped_path = self.original_wallpaper.replace("'", "'\\''")
            subprocess.run(
                f"gsettings set org.cinnamon.desktop.background picture-uri 'file://{escaped_path}'",
                shell=True, check=False
            )
        return False

    def key_pressed(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_Escape:
            self.window.close()
            return True
        if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            focused = self.window.get_focus()
            if isinstance(focused, Gtk.FlowBoxChild):
                button = focused.get_child()
                if isinstance(button, Gtk.Button):
                    button.activate()
                    return True
        return False


app = WallpaperPicker()
app.run(None)