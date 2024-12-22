import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps


# README
#export command in terminal:  pyinstaller winapp.py --onefile --windowed

class CollageMakerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Escape's V-Collage Maker ver0.3")
        self.images = []  # List of (image, filename) tuples
        self.preview_image = None

        # Collage settings
        self.collage_width = tk.IntVar(value=1280)
        self.border_width = tk.IntVar(value=0)
        self.border_color = "White"  # Default to white

        # Primary colors
        self.primary_colors = {
            "Black": (0, 0, 0),
            "White": (255, 255, 255),
            "Red": (255, 0, 0),
            "Green": (0, 255, 0),
            "Blue": (0, 0, 255),
            "Yellow": (255, 255, 0),
            "Cyan": (0, 255, 255),
            "Magenta": (255, 0, 255),
        }

        # UI Elements
        self.create_widgets()
        self.update_preview()  # Initial blank preview

    def create_widgets(self):

        # Right Frame
        right_frame = tk.Frame(self.root)
        right_frame.pack(side="right", padx=5, pady=5, fill="both", expand=True)

        # Preview Area
        self.preview_label = tk.Label(right_frame, text="Preview will appear here")
        self.preview_label.pack(pady=10)


        # Upload Images Button
        upload_button = tk.Button(self.root, text="Upload Images", command=self.upload_images)
        upload_button.pack(pady=10)

        # Listbox for image management
        self.image_listbox = tk.Listbox(self.root, selectmode=tk.SINGLE, height=10, width=40)
        self.image_listbox.pack(pady=10)

        # Image management buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)

        remove_button = tk.Button(button_frame, text="Remove Image", command=self.remove_image)
        remove_button.grid(row=0, column=0, padx=5)

        clear_all_button = tk.Button(button_frame, text="Clear All Images", command=self.clear_all_images)
        clear_all_button.grid(row=1, column=0, padx=5)

        move_up_button = tk.Button(button_frame, text="Move Up", command=self.move_image_up)
        move_up_button.grid(row=0, column=1, padx=5)

        move_down_button = tk.Button(button_frame, text="Move Down", command=self.move_image_down)
        move_down_button.grid(row=1, column=1, padx=5)

        # Settings Frame
        settings_frame = tk.Frame(self.root)
        settings_frame.pack(pady=10)

        tk.Label(settings_frame, text="Collage Width:").grid(row=0, column=0)
        collage_width_entry = tk.Entry(settings_frame, textvariable=self.collage_width)
        collage_width_entry.grid(row=0, column=1)
        collage_width_entry.bind("<KeyRelease>", lambda e: self.update_preview())  # Trigger preview on change

        tk.Label(settings_frame, text="Border Width:").grid(row=1, column=0)
        border_width_entry = tk.Entry(settings_frame, textvariable=self.border_width)
        border_width_entry.grid(row=1, column=1)
        border_width_entry.bind("<KeyRelease>", lambda e: self.update_preview())  # Trigger preview on change

        # Dropdown for border color
        tk.Label(settings_frame, text="Border Color:").grid(row=2, column=0)
        self.border_color_dropdown = tk.StringVar(value="White")  # Default to White
        color_menu = tk.OptionMenu(
            settings_frame, self.border_color_dropdown, *self.primary_colors.keys(), command=self.update_preview
        )
        color_menu.grid(row=2, column=1)

        # Export Button
        export_button = tk.Button(self.root, text="Export Collage", command=self.export_collage)
        export_button.pack(pady=5)


    def upload_images(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg *.jpeg *.png *.webp *.jfif")])
        if file_paths:
            for file_path in file_paths:
                image = Image.open(file_path)
                self.images.append((image, file_path))
                self.image_listbox.insert(tk.END, file_path.split("/")[-1])  # Add filename to listbox
            self.update_preview()  # Update preview

    def remove_image(self):
        selected_index = self.image_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            self.images.pop(index)  # Remove image from list
            self.image_listbox.delete(index)  # Remove from listbox
            self.update_preview()  # Update preview

    def clear_all_images(self):
        self.images.clear()  # Clear the image list
        self.image_listbox.delete(0, tk.END)  # Clear the listbox
        self.update_preview()  # Update preview

    def move_image_up(self):
        selected_index = self.image_listbox.curselection()
        if selected_index and selected_index[0] > 0:
            index = selected_index[0]
            # Swap images in the list
            self.images[index], self.images[index - 1] = self.images[index - 1], self.images[index]
            # Update listbox
            self.update_listbox()
            self.image_listbox.select_set(index - 1)  # Keep selection on the moved item
            self.update_preview()  # Update preview

    def move_image_down(self):
        selected_index = self.image_listbox.curselection()
        if selected_index and selected_index[0] < len(self.images) - 1:
            index = selected_index[0]
            # Swap images in the list
            self.images[index], self.images[index + 1] = self.images[index + 1], self.images[index]
            # Update listbox
            self.update_listbox()
            self.image_listbox.select_set(index + 1)  # Keep selection on the moved item
            self.update_preview()  # Update preview

    def update_listbox(self):
        self.image_listbox.delete(0, tk.END)  # Clear listbox
        for _, file_path in self.images:
            self.image_listbox.insert(tk.END, file_path.split("/")[-1])  # Re-add filenames to listbox

    def update_preview(self, *_):
        if not self.images:
            self.preview_label.config(image='', text="Preview will appear here")
            return

        selected_color = self.primary_colors[self.border_color_dropdown.get()]  # Get selected color
        collage = self.create_collage([img for img, _ in self.images], self.collage_width.get(), self.border_width.get(), selected_color)
        self.show_preview(collage)

    def show_preview(self, collage):
        preview = collage.copy()
        preview.thumbnail((300, 1000))
        self.preview_image = ImageTk.PhotoImage(preview)
        self.preview_label.config(image=self.preview_image, text='')

    def create_collage(self, images, collage_width, border_width, border_color):
        resized_images = []

        for img in images:
            aspect_ratio = img.height / img.width
            new_height = int(collage_width * aspect_ratio)
            resized_img = img.resize((collage_width, new_height))

            if border_width > 0:
                resized_img = ImageOps.expand(resized_img, border=border_width, fill=border_color)

            resized_images.append(resized_img)

        collage_height = sum(img.height for img in resized_images)
        collage = Image.new('RGB', (collage_width, collage_height), (255, 255, 255))

        y_offset = 0
        for img in resized_images:
            collage.paste(img, (-border_width, y_offset))
            y_offset += img.height

        return collage

    def export_collage(self):
        if not self.images:
            messagebox.showwarning("Warning", "Please upload images first.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"),("WEBP", "*.webp"),("JFIF", "*.jfif")])
        if file_path:
            selected_color = self.primary_colors[self.border_color_dropdown.get()]  # Get selected color
            collage = self.create_collage([img for img, _ in self.images], self.collage_width.get(), self.border_width.get(), selected_color)
            collage.save(file_path)
            messagebox.showinfo("Success", "Collage saved successfully!")


# Run the app
root = tk.Tk()
app = CollageMakerApp(root)
root.mainloop()
