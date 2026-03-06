def register(editor):
    def make_uppercase():
        # 1. Ask the editor for the currently active tab's text area
        text_widget = editor.get_active_text()
        if not text_widget:
            return
            
        # 2. Grab the text, modify it, and put it back
        content = text_widget.get("1.0", "end-1c")
        text_widget.delete("1.0", "end")
        text_widget.insert("1.0", content.upper())

    # 3. Add the button to the Plugin Menu
    editor.plugin_menu.add_command(label="Convert to Uppercase", command=make_uppercase)