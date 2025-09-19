# @title   : ImageCoordinatePicker.py
# -*- coding:utf-8 -*-
# @author  : TokitaYitsuki
# @URL : https://github.com/TokitaYitsuki/ImageCoordinatePicker-To-Renpy
# @Date    : 9-12-2025
# @Description: This is a program made with Python that helps Ren'Py developers arrange the UI and confirm the UI's position relative to the background coordinates.
# @Version : V1.2
# @License : MIT License

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog

from PIL import Image, ImageTk


class DraggableImage:
    def __init__(self, canvas, original_image, bg_scale_x, bg_scale_y, bg_x, bg_y, name="叠加图片", x=0, y=0):
        self.canvas = canvas
        self.original_image = original_image
        self.bg_scale_x = bg_scale_x
        self.bg_scale_y = bg_scale_y
        self.bg_x = bg_x
        self.bg_y = bg_y
        self.name = name
        self.is_dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.is_locked = False
        self.is_selected = False  # 跟踪选中状态

        # 计算缩放后的尺寸(与背景图片相同的缩放比例)
        self.scaled_width = int(round(original_image.width / bg_scale_x))
        self.scaled_height = int(round(original_image.height / bg_scale_y))

        # 缩放图片
        self.scaled_image = original_image.resize(
            (self.scaled_width, self.scaled_height),
            Image.Resampling.LANCZOS
        )

        # 创建图像副本
        self.photo = ImageTk.PhotoImage(self.scaled_image)

        # 将背景坐标转换为画布坐标(使用四舍五入减少误差)
        canvas_x = bg_x + int(round(x / bg_scale_x))
        canvas_y = bg_y + int(round(y / bg_scale_y))

        # 在画布上创建图像对象
        self.canvas_id = self.canvas.create_image(
            canvas_x, canvas_y, anchor=tk.NW, image=self.photo, tags=("draggable", "overlay")
        )

        # 存储背景坐标(相对于背景图片左上角)
        self.bg_coord_x = x
        self.bg_coord_y = y

        # 绑定事件
        self.canvas.tag_bind(self.canvas_id, "<Button-1>", self.on_press)
        self.canvas.tag_bind(self.canvas_id, "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind(self.canvas_id, "<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        #####鼠标按下事件#####
        if self.is_locked:
            return

        self.is_dragging = True
        # 计算鼠标相对于图片左上角的偏移
        coords = self.canvas.coords(self.canvas_id)
        self.drag_offset_x = event.x - coords[0]
        self.drag_offset_y = event.y - coords[1]
        # 将当前图片置于顶层
        self.canvas.tag_raise(self.canvas_id)

        # 选中当前图片
        self.set_selected(True)

        # 通知父组件选中此图片
        if hasattr(self, 'parent_app'):
            self.parent_app.select_image_by_reference(self)

    def on_drag(self, event):
        #####鼠标拖动事件#####
        if self.is_locked:
            return  # 如果锁定，不响应拖动

        if self.is_dragging:
            # 更新图片位置
            new_x = event.x - self.drag_offset_x
            new_y = event.y - self.drag_offset_y
            self.canvas.coords(self.canvas_id, new_x, new_y)

            # 更新背景坐标 - 使用四舍五入减少误差
            self.bg_coord_x = int(round((new_x - self.bg_x) * self.bg_scale_x))
            self.bg_coord_y = int(round((new_y - self.bg_y) * self.bg_scale_y))

            # 更新列表中的坐标显示
            if hasattr(self, 'parent_app'):
                self.parent_app.update_image_list_item(self)
                self.parent_app.update_coord_list_from_images()

    def on_release(self, event):
        #####鼠标释放事件#####
        if self.is_locked:
            return

        self.is_dragging = False

        # 更新坐标点列表
        if hasattr(self, 'parent_app'):
            self.parent_app.update_coord_list_from_images()

    def get_bg_coordinates(self):
        #####获取图片在背景上的坐标#####
        return self.bg_coord_x, self.bg_coord_y

    def update_position(self, bg_x, bg_y, bg_scale_x, bg_scale_y, canvas_bg_x, canvas_bg_y):
        #####更新图片位置(基于背景坐标)#####
        # 更新缩放比例
        self.bg_scale_x = bg_scale_x
        self.bg_scale_y = bg_scale_y
        self.bg_x = canvas_bg_x
        self.bg_y = canvas_bg_y

        # 重新计算缩放后的尺寸 - 使用四舍五入减少误差
        self.scaled_width = int(round(self.original_image.width / bg_scale_x))
        self.scaled_height = int(round(self.original_image.height / bg_scale_y))

        # 缩放图片
        self.scaled_image = self.original_image.resize(
            (self.scaled_width, self.scaled_height),
            Image.Resampling.LANCZOS
        )

        # 更新图片
        self.photo = ImageTk.PhotoImage(self.scaled_image)

        # 计算画布坐标(使用四舍五入减少误差)
        canvas_x = canvas_bg_x + int(round(bg_x / bg_scale_x))
        canvas_y = canvas_bg_y + int(round(bg_y / bg_scale_y))

        # 更新画布上的图片
        self.canvas.itemconfig(self.canvas_id, image=self.photo)
        self.canvas.coords(self.canvas_id, canvas_x, canvas_y)

        # 更新背景坐标
        self.bg_coord_x = bg_x
        self.bg_coord_y = bg_y

    def set_position_by_bg_coords(self, bg_x, bg_y):
        #####通过背景坐标设置图片位置#####
        # 计算画布坐标 - 使用四舍五入减少误差
        canvas_x = self.bg_x + int(round(bg_x / self.bg_scale_x))
        canvas_y = self.bg_y + int(round(bg_y / self.bg_scale_y))

        # 更新位置
        self.canvas.coords(self.canvas_id, canvas_x, canvas_y)

        # 更新背景坐标
        self.bg_coord_x = bg_x
        self.bg_coord_y = bg_y

        # 更新列表中的坐标显示
        if hasattr(self, 'parent_app'):
            self.parent_app.update_image_list_item(self)
            self.parent_app.update_coord_list_from_images()

    def set_locked(self, locked):
        #####设置锁定状态#####
        self.is_locked = locked

    def set_selected(self, selected):
        #####设置选中状态#####
        self.is_selected = selected
        # 不再添加背景边框，只更新选中状态

    def set_parent_app(self, parent_app):
        #####设置父应用程序引用#####
        self.parent_app = parent_app


class ImageCoordinatePicker:
    def __init__(self, root):
        self.root = root
        self.root.title("叠加图片坐标拾取")
        width, height = 1400, 800
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.root.geometry(size)


        # 存储图片和坐标点
        self.background_image = None
        self.draggable_images = []  # 存储所有可拖动图片
        self.points = []  # 存储坐标点
        self.current_mode = "coordinate"  # 当前模式: "coordinate" 或 "overlay"

        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 创建左右分栏
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))

        # 使用Canvas来显示图片
        self.canvas = tk.Canvas(left_frame, bg="white", width=600, height=500)
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.canvas.bind("<Button-1>", self.canvas_clicked)
        self.canvas.bind("<Motion>", self.canvas_mouse_move)

        # 信息显示标签
        self.info_label = ttk.Label(left_frame, text="坐标: (0, 0) - 模式: 坐标获取")
        self.info_label.grid(row=1, column=0, sticky=tk.W, pady=5)

        # 按钮区域
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)

        self.load_bg_button = ttk.Button(button_frame, text="加载背景图片", command=self.load_background_image)
        self.load_bg_button.grid(row=0, column=0, padx=(0, 5))

        self.add_image_button = ttk.Button(button_frame, text="添加叠加图片", command=self.add_draggable_image)
        self.add_image_button.grid(row=0, column=1, padx=5)

        self.batch_add_images_button = ttk.Button(button_frame, text="批量添加图片", command=self.batch_add_images)
        self.batch_add_images_button.grid(row=0, column=2, padx=5)

        self.clear_points_button = ttk.Button(button_frame, text="清除坐标点", command=self.clear_points)
        self.clear_points_button.grid(row=0, column=3, padx=5)

        self.import_coords_button = ttk.Button(button_frame, text="导入坐标", command=self.import_coordinates)
        self.import_coords_button.grid(row=0, column=4, padx=5)

        self.mode_button = ttk.Button(button_frame, text="切换到叠加图片模式", command=self.toggle_mode)
        self.mode_button.grid(row=0, column=5, padx=5)

        self.save_button = ttk.Button(button_frame, text="保存数据", command=self.save_data)
        self.save_button.grid(row=0, column=6, padx=(5, 0))

        # 右侧控制面板
        right_panel = ttk.LabelFrame(right_frame, text="控制面板", padding="5")
        right_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 叠加图片列表
        ttk.Label(right_panel, text="叠加图片列表:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.image_listbox = tk.Listbox(right_panel, height=10, width=40)
        self.image_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        self.image_listbox.bind("<<ListboxSelect>>", self.on_image_selected)

        # 图片控制按钮
        image_control_frame = ttk.Frame(right_panel)
        image_control_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.set_position_button = ttk.Button(image_control_frame, text="设置坐标", command=self.set_image_position)
        self.set_position_button.grid(row=0, column=0, padx=(0, 5))

        self.lock_image_button = ttk.Button(image_control_frame, text="锁定叠加图片", command=self.toggle_image_lock)
        self.lock_image_button.grid(row=0, column=1, padx=5)

        self.remove_image_button = ttk.Button(image_control_frame, text="删除图片", command=self.remove_selected_image)
        self.remove_image_button.grid(row=0, column=2, padx=5)

        self.rename_image_button = ttk.Button(image_control_frame, text="重命名", command=self.rename_selected_image)
        self.rename_image_button.grid(row=0, column=3, padx=5)

        self.bring_to_top_button = ttk.Button(image_control_frame, text="置顶", command=self.bring_images_to_top)
        self.bring_to_top_button.grid(row=0, column=4, padx=5)

        # 坐标点列表
        ttk.Label(right_panel, text="坐标点列表:").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))

        self.coord_list = tk.Listbox(right_panel, height=10, width=40)
        self.coord_list.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        self.coord_list.bind("<<ListboxSelect>>", self.on_coord_selected)

        # 坐标点控制按钮
        coord_control_frame = ttk.Frame(right_panel)
        coord_control_frame.grid(row=5, column=0, sticky=(tk.W, tk.E))

        self.add_point_button = ttk.Button(coord_control_frame, text="添加坐标", command=self.add_coordinate_point)
        self.add_point_button.grid(row=0, column=0, padx=(0, 5))

        self.edit_point_button = ttk.Button(coord_control_frame, text="修改坐标", command=self.edit_selected_point)
        self.edit_point_button.grid(row=0, column=1, padx=5)

        self.remove_point_button = ttk.Button(coord_control_frame, text="删除坐标", command=self.remove_selected_point)
        self.remove_point_button.grid(row=0, column=2, padx=5)

        # 配置权重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=3)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        right_panel.rowconfigure(4, weight=1)

        # 存储图片显示位置和缩放比例
        self.bg_x = 0
        self.bg_y = 0
        self.bg_scale_x = 1.0
        self.bg_scale_y = 1.0

        # 当前选中的叠加图片
        self.selected_image_index = -1

        # 背景图片的Canvas ID
        self.bg_image_id = None


    def batch_add_images(self):
        #####批量添加叠加图片#####
        if not self.background_image:
            messagebox.showwarning("警告", "请先加载背景图片")
            return

        file_paths = filedialog.askopenfilenames(
            title="选择要添加的图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )

        if not file_paths:
            return

        for file_path in file_paths:
            try:
                image = Image.open(file_path)
                # 使用文件名(不含扩展名)作为图片名称
                name = os.path.splitext(os.path.basename(file_path))[0]

                # 默认位置在画布中央(背景坐标)
                bg_width, bg_height = self.background_image.size
                bg_x = bg_width // 2 - image.width // 2
                bg_y = bg_height // 2 - image.height // 2

                # 创建可拖动图片
                draggable_image = DraggableImage(
                    self.canvas, image,
                    self.bg_scale_x, self.bg_scale_y,
                    self.bg_x, self.bg_y,
                    name, bg_x, bg_y
                )
                draggable_image.set_parent_app(self)

                self.draggable_images.append(draggable_image)

                # 添加到列表
                self.add_image_to_list(draggable_image)

            except Exception as e:
                messagebox.showerror("错误", f"无法加载图片 {file_path}: {str(e)}")

        # 更新坐标点列表
        if self.current_mode == "overlay":
            self.update_coord_list_from_images()

        # 确保背景图片始终在底层
        self.canvas.tag_lower(self.bg_image_id)

    def center_window(self, window, width, height):
        #####控制窗口生成于屏幕中央#####
        screenwidth = window.winfo_screenwidth()
        screenheight = window.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        window.geometry(size)

    def import_coordinates(self):
        #####从文本文件导入坐标点#####
        if self.current_mode != "coordinate":
            messagebox.showwarning("警告", "请在坐标获取模式下使用此功能")
            return

        file_path = filedialog.askopenfilename(
            title="选择坐标文件",
            filetypes=[("文本文件", "*.txt")]
        )

        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            added_count = 0
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # 处理不同的分隔符(逗号、空格、中文逗号等)
                if '，' in line:  # 中文逗号
                    parts = line.split('，')
                elif ',' in line:  # 英文逗号
                    parts = line.split(',')
                else:
                    # 尝试按空格分割
                    parts = line.split()

                if len(parts) >= 2:
                    try:
                        x = int(parts[0].strip())
                        y = int(parts[1].strip())

                        # 添加到点列表
                        self.points.append((x, y))
                        self.coord_list.insert(tk.END, f"({x}, {y})")

                        # 在Canvas上绘制点
                        self.draw_point(x, y)

                        added_count += 1
                    except ValueError:
                        # 跳过无法解析的行
                        continue

            messagebox.showinfo("成功", f"成功导入 {added_count} 个坐标点")

        except Exception as e:
            messagebox.showerror("错误", f"导入坐标时出错: {str(e)}")

    def toggle_mode(self):
        #####切换模式#####
        if self.current_mode == "coordinate":
            # 切换到叠加图片模式
            self.current_mode = "overlay"
            self.mode_button.config(text="切换到坐标获取模式")
            self.info_label.config(text="模式: 叠加图片")

            # 重新加载所有叠加图片，确保它们显示在背景图片之上
            self.reload_overlay_images()

            # 更新坐标点列表
            self.update_coord_list_from_images()

            # 禁用坐标点相关功能
            self.add_point_button.config(state=tk.DISABLED)
            self.edit_point_button.config(state=tk.DISABLED)
            self.remove_point_button.config(state=tk.DISABLED)

        else:
            # 切换到坐标获取模式
            self.current_mode = "coordinate"
            self.mode_button.config(text="切换到叠加图片模式")
            self.info_label.config(text="模式: 坐标获取")

            # 重新显示背景图片，确保它显示在叠加图片之上
            if self.background_image:
                self.display_background_image()

            # 启用坐标点相关功能
            self.add_point_button.config(state=tk.NORMAL)
            self.edit_point_button.config(state=tk.NORMAL)
            self.remove_point_button.config(state=tk.NORMAL)

    def update_coord_list_from_images(self):
        #####从叠加图片更新坐标点列表#####
        self.coord_list.delete(0, tk.END)
        self.points = []

        for img in self.draggable_images:
            x, y = img.get_bg_coordinates()
            self.points.append((x, y))
            self.coord_list.insert(tk.END, f"({x}, {y})")

    def reload_overlay_images(self):
        #####重新加载所有叠加图片，确保它们显示在背景图片之上#####
        if not self.background_image:
            return

        # 清除所有叠加图片
        for img in self.draggable_images:
            self.canvas.delete(img.canvas_id)

        # 重新创建所有叠加图片
        for img in self.draggable_images:
            # 创建新的可拖动图片
            new_img = DraggableImage(
                self.canvas, img.original_image,
                self.bg_scale_x, self.bg_scale_y,
                self.bg_x, self.bg_y,
                img.name, img.bg_coord_x, img.bg_coord_y
            )
            new_img.set_locked(img.is_locked)
            new_img.set_parent_app(self)

            # 替换旧的图片对象
            index = self.draggable_images.index(img)
            self.draggable_images[index] = new_img

        # 确保叠加图片显示在背景图片之上
        self.canvas.tag_raise("overlay")

    def load_background_image(self):
        #####加载背景图片#####
        file_path = filedialog.askopenfilename(
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path:
            try:
                self.background_image = Image.open(file_path)
                self.display_background_image()
                self.points = []
                self.coord_list.delete(0, tk.END)

                # 清除所有叠加图片
                for img in self.draggable_images:
                    self.canvas.delete(img.canvas_id)
                self.draggable_images = []
                self.image_listbox.delete(0, tk.END)

                # 重置模式
                self.current_mode = "coordinate"
                self.mode_button.config(text="切换到叠加图片模式")
                self.info_label.config(text="模式: 坐标获取")

                # 启用坐标点相关功能
                self.add_point_button.config(state=tk.NORMAL)
                self.edit_point_button.config(state=tk.NORMAL)
                self.remove_point_button.config(state=tk.NORMAL)

            except Exception as e:
                messagebox.showerror("错误", f"无法加载图片: {str(e)}")

    def display_background_image(self):
        #####显示背景图片#####
        if self.background_image:
            # 获取Canvas的当前尺寸
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # 如果Canvas还没有被渲染，使用默认尺寸
            if canvas_width < 10:
                canvas_width = 600
            if canvas_height < 10:
                canvas_height = 500

            # 计算缩放比例，保持宽高比
            img_width, img_height = self.background_image.size
            width_ratio = canvas_width / img_width
            height_ratio = canvas_height / img_height
            scale_ratio = min(width_ratio, height_ratio)

            # 计算缩放后的尺寸
            new_width = int(img_width * scale_ratio)
            new_height = int(img_height * scale_ratio)

            # 缩放图片
            display_image = self.background_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(display_image)

            # 计算图片在Canvas中的位置(居中显示)
            self.bg_x = (canvas_width - new_width) // 2
            self.bg_y = (canvas_height - new_height) // 2

            # 清除Canvas上的叠加图片和点，但保留背景图片
            self.canvas.delete("overlay")
            self.canvas.delete("point")
            self.canvas.delete("point_text")

            # 如果背景图片不存在，则创建它
            if self.bg_image_id is None:
                self.bg_image_id = self.canvas.create_image(
                    self.bg_x, self.bg_y, anchor=tk.NW, image=self.bg_photo, tags="background"
                )
            else:
                # 更新背景图片
                self.canvas.itemconfig(self.bg_image_id, image=self.bg_photo)
                self.canvas.coords(self.bg_image_id, self.bg_x, self.bg_y)

            # 将背景图片置于底层
            self.canvas.tag_lower(self.bg_image_id)

            # 存储缩放比例，用于坐标转换
            self.bg_scale_x = img_width / new_width
            self.bg_scale_y = img_height / new_height

            # 重新绘制已有点和叠加图片
            self.redraw_points()
            for img in self.draggable_images:
                img.update_position(
                    img.bg_coord_x, img.bg_coord_y,
                    self.bg_scale_x, self.bg_scale_y,
                    self.bg_x, self.bg_y
                )
                img.set_parent_app(self)  # 设置父应用程序引用

    def add_draggable_image(self):
        #####添加可拖动的叠加图片#####
        if not self.background_image:
            messagebox.showwarning("警告", "请先加载背景图片")
            return

        file_path = filedialog.askopenfilename(
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path:
            try:
                image = Image.open(file_path)
                # 使用文件名(不含扩展名)作为图片名称
                name = os.path.splitext(os.path.basename(file_path))[0]

                # 默认位置在画布中央(背景坐标)
                bg_width, bg_height = self.background_image.size
                bg_x = bg_width // 2 - image.width // 2
                bg_y = bg_height // 2 - image.height // 2

                # 创建可拖动图片
                draggable_image = DraggableImage(
                    self.canvas, image,
                    self.bg_scale_x, self.bg_scale_y,
                    self.bg_x, self.bg_y,
                    name, bg_x, bg_y
                )
                draggable_image.set_parent_app(self)

                self.draggable_images.append(draggable_image)

                # 添加到列表
                self.add_image_to_list(draggable_image)

                # 更新坐标点列表
                if self.current_mode == "overlay":
                    self.update_coord_list_from_images()

                # 确保背景图片始终在底层
                self.canvas.tag_lower(self.bg_image_id)

            except Exception as e:
                messagebox.showerror("错误", f"无法加载图片: {str(e)}")

    def add_image_to_list(self, image):
        #####添加图片到列表#####
        bg_x, bg_y = image.get_bg_coordinates()
        item_text = f"{image.name} - ({bg_x}, {bg_y})"
        self.image_listbox.insert(tk.END, item_text)

    def update_image_list_item(self, image):
        #####更新列表中的图片项#####
        if image in self.draggable_images:
            index = self.draggable_images.index(image)
            bg_x, bg_y = image.get_bg_coordinates()
            item_text = f"{image.name} - ({bg_x}, {bg_y})"
            self.image_listbox.delete(index)
            self.image_listbox.insert(index, item_text)
            self.image_listbox.select_set(index)

    def on_image_selected(self, event):
        #####当选择叠加图片时#####
        selection = self.image_listbox.curselection()
        if selection:
            self.selected_image_index = selection[0]
            # 取消之前选中的图片
            for img in self.draggable_images:
                img.set_selected(False)

            # 选中当前图片
            if self.selected_image_index < len(self.draggable_images):
                selected_image = self.draggable_images[self.selected_image_index]
                selected_image.set_selected(True)
                # 确保选中的图片显示在最上层
                self.canvas.tag_raise(selected_image.canvas_id)

    def select_image_by_reference(self, image):
        #####通过图片引用选择图片#####
        if image in self.draggable_images:
            index = self.draggable_images.index(image)
            self.image_listbox.select_clear(0, tk.END)
            self.image_listbox.select_set(index)
            self.selected_image_index = index

            # 取消之前选中的图片
            for img in self.draggable_images:
                img.set_selected(False)

            # 选中当前图片
            image.set_selected(True)

    def toggle_image_lock(self):
        #####切换选中图片的锁定状态#####
        if self.selected_image_index < 0 or self.selected_image_index >= len(self.draggable_images):
            messagebox.showwarning("警告", "请先选择一个叠加图片")
            return

        image = self.draggable_images[self.selected_image_index]
        image.set_locked(not image.is_locked)

        # 更新按钮文本
        if image.is_locked:
            self.lock_image_button.config(text="解锁叠加图片")
        else:
            self.lock_image_button.config(text="锁定叠加图片")

    def set_image_position(self):
        #####设置选中图片的位置(通过输入背景坐标)#####
        if self.selected_image_index < 0 or self.selected_image_index >= len(self.draggable_images):
            messagebox.showwarning("警告", "请先选择一个叠加图片")
            return

        # 获取当前图片的背景坐标
        current_x, current_y = self.draggable_images[self.selected_image_index].get_bg_coordinates()

        # 创建输入对话框
        input_dialog = tk.Toplevel(self.root)
        input_dialog.title("设置图片位置")
        self.center_window(input_dialog, 300, 150)
        input_dialog.transient(self.root)
        input_dialog.grab_set()

        # 输入框
        ttk.Label(input_dialog, text="X坐标:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        x_var = tk.StringVar(value=str(current_x))
        x_entry = ttk.Entry(input_dialog, textvariable=x_var)
        x_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W + tk.E)

        ttk.Label(input_dialog, text="Y坐标:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        y_var = tk.StringVar(value=str(current_y))
        y_entry = ttk.Entry(input_dialog, textvariable=y_var)
        y_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W + tk.E)

        # 确定按钮
        def confirm():
            try:
                x = int(x_var.get())
                y = int(y_var.get())

                # 更新图片位置
                self.draggable_images[self.selected_image_index].set_position_by_bg_coords(x, y)
                input_dialog.destroy()

                # 更新坐标点列表
                if self.current_mode == "overlay":
                    self.update_coord_list_from_images()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的整数坐标")

        ttk.Button(input_dialog, text="确定", command=confirm).grid(row=2, column=0, columnspan=2, pady=10)

        # 配置权重
        input_dialog.columnconfigure(1, weight=1)

    def remove_selected_image(self):
        #####删除选中的叠加图片#####
        if 0 <= self.selected_image_index < len(self.draggable_images):
            # 从画布中删除
            self.canvas.delete(self.draggable_images[self.selected_image_index].canvas_id)
            # 从列表中删除
            del self.draggable_images[self.selected_image_index]
            # 从列表框中删除
            self.image_listbox.delete(self.selected_image_index)
            self.selected_image_index = -1

            # 更新坐标点列表
            if self.current_mode == "overlay":
                self.update_coord_list_from_images()

    def rename_selected_image(self):
        #####重命名选中的叠加图片#####
        if 0 <= self.selected_image_index < len(self.draggable_images):
            current_name = self.draggable_images[self.selected_image_index].name
            new_name = simpledialog.askstring(" ", "请输入新名称:", initialvalue=current_name)
            if new_name:
                self.draggable_images[self.selected_image_index].name = new_name
                self.update_image_list_item(self.draggable_images[self.selected_image_index])

    def bring_images_to_top(self):
        #####将所有叠加图片置顶#####
        if not self.background_image:
            return

        # 清除所有叠加图片
        for img in self.draggable_images:
            self.canvas.delete(img.canvas_id)

        # 重新创建所有叠加图片
        for img in self.draggable_images:
            # 创建新的可拖动图片
            new_img = DraggableImage(
                self.canvas, img.original_image,
                self.bg_scale_x, self.bg_scale_y,
                self.bg_x, self.bg_y,
                img.name, img.bg_coord_x, img.bg_coord_y
            )
            new_img.set_locked(img.is_locked)
            new_img.set_parent_app(self)

            # 替换旧的图片对象
            index = self.draggable_images.index(img)
            self.draggable_images[index] = new_img

        # 确保叠加图片显示在背景图片之上
        self.canvas.tag_raise("overlay")

    def add_coordinate_point(self):
        #####添加坐标点#####
        if not self.background_image:
            messagebox.showwarning("警告", "请先加载背景图片")
            return

        # 创建输入对话框
        input_dialog = tk.Toplevel(self.root)
        input_dialog.title("添加坐标点")
        self.center_window(input_dialog, 300, 150)
        input_dialog.transient(self.root)
        input_dialog.grab_set()

        # 输入框
        ttk.Label(input_dialog, text="X坐标:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        x_var = tk.StringVar(value="0")
        x_entry = ttk.Entry(input_dialog, textvariable=x_var)
        x_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W + tk.E)

        ttk.Label(input_dialog, text="Y坐标:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        y_var = tk.StringVar(value="0")
        y_entry = ttk.Entry(input_dialog, textvariable=y_var)
        y_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W + tk.E)

        # 确定按钮
        def confirm():
            try:
                x = int(x_var.get())
                y = int(y_var.get())

                # 添加到点列表
                self.points.append((x, y))
                self.coord_list.insert(tk.END, f"({x}, {y})")

                # 在Canvas上绘制点
                self.draw_point(x, y)

                input_dialog.destroy()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的整数坐标")

        ttk.Button(input_dialog, text="确定", command=confirm).grid(row=2, column=0, columnspan=2, pady=10)

        # 配置权重
        input_dialog.columnconfigure(1, weight=1)

    def on_coord_selected(self, event):
        #####当选择坐标点时#####
        selection = self.coord_list.curselection()
        if selection:
            index = selection[0]
            if index < len(self.points):
                x, y = self.points[index]
                self.info_label.config(text=f"选中坐标: ({x}, {y})")

    def edit_selected_point(self):
        #####修改选中的坐标点#####
        selection = self.coord_list.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个坐标点")
            return

        index = selection[0]
        if index >= len(self.points):
            return

        # 获取当前坐标
        current_x, current_y = self.points[index]

        # 创建输入对话框
        input_dialog = tk.Toplevel(self.root)
        input_dialog.title("修改坐标点")
        self.center_window(input_dialog, 300, 150)
        input_dialog.transient(self.root)
        input_dialog.grab_set()

        # 输入框
        ttk.Label(input_dialog, text="X坐标:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        x_var = tk.StringVar(value=str(current_x))
        x_entry = ttk.Entry(input_dialog, textvariable=x_var)
        x_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W + tk.E)

        ttk.Label(input_dialog, text="Y坐标:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        y_var = tk.StringVar(value=str(current_y))
        y_entry = ttk.Entry(input_dialog, textvariable=y_var)
        y_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W + tk.E)

        # 确定按钮
        def confirm():
            try:
                x = int(x_var.get())
                y = int(y_var.get())

                # 更新点列表
                self.points[index] = (x, y)
                self.coord_list.delete(index)
                self.coord_list.insert(index, f"({x}, {y})")

                # 重新绘制所有点
                self.canvas.delete("point")
                self.canvas.delete("point_text")
                self.redraw_points()

                input_dialog.destroy()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的整数坐标")

        ttk.Button(input_dialog, text="确定", command=confirm).grid(row=2, column=0, columnspan=2, pady=10)

        # 配置权重
        input_dialog.columnconfigure(1, weight=1)

    def canvas_clicked(self, event):
        #####Canvas点击事件#####
        if self.current_mode == "overlay":
            return

        # 检查是否点击了背景图片区域
        if (self.background_image and
                self.bg_x <= event.x < self.bg_x + self.bg_photo.width() and
                self.bg_y <= event.y < self.bg_y + self.bg_photo.height()):

            # 计算原始图片上的坐标(使用四舍五入减少误差)
            x = int(round((event.x - self.bg_x) * self.bg_scale_x))
            y = int(round((event.y - self.bg_y) * self.bg_scale_y))

            # 限制坐标在图片范围内
            x = max(0, min(x, self.background_image.width - 1))
            y = max(0, min(y, self.background_image.height - 1))

            # 添加到点列表
            self.points.append((x, y))
            self.coord_list.insert(tk.END, f"({x}, {y})")

            # 获取像素颜色
            rgb = self.background_image.getpixel((x, y))
            if isinstance(rgb, int):  # 灰度图像处理
                rgb = (rgb, rgb, rgb)
            self.info_label.config(text=f"坐标: ({x}, {y}), RGB: {rgb}")

            # 在Canvas上绘制点
            self.draw_point(x, y)

            # 确保背景图片始终在底层
            self.canvas.tag_lower(self.bg_image_id)

    def draw_point(self, orig_x, orig_y):
        #####在Canvas上绘制一个点#####
        # 转换坐标到Canvas上的位置(使用四舍五入减少误差)
        canvas_x = self.bg_x + int(round(orig_x / self.bg_scale_x))
        canvas_y = self.bg_y + int(round(orig_y / self.bg_scale_y))

        # 绘制点
        radius = 3
        self.canvas.create_oval(
            canvas_x - radius, canvas_y - radius,
            canvas_x + radius, canvas_y + radius,
            fill="red", outline="red", tags=("point", "overlay")
        )

        # 绘制坐标文本
        self.canvas.create_text(
            canvas_x + 10, canvas_y - 10,
            text=f"({orig_x}, {orig_y})",
            fill="black", anchor=tk.NW, tags=("point_text", "overlay")
        )

        # 确保点和文本在叠加图片之上
        self.canvas.tag_raise("point")
        self.canvas.tag_raise("point_text")

        # 确保背景图片始终在底层
        self.canvas.tag_lower(self.bg_image_id)

    def redraw_points(self):
        #####重新绘制所有点#####
        for x, y in self.points:
            self.draw_point(x, y)

    def canvas_mouse_move(self, event):
        #####Canvas鼠标移动事件#####
        # 如果在叠加图片模式下，不显示背景坐标信息
        if self.current_mode == "overlay":
            mode_text = "叠加图片"
            self.info_label.config(text=f"模式: {mode_text}")
            return

        if self.background_image:
            # 检查鼠标是否在背景图片区域内
            if (self.bg_x <= event.x < self.bg_x + self.bg_photo.width() and
                    self.bg_y <= event.y < self.bg_y + self.bg_photo.height()):

                # 计算原始图片上的坐标(使用四舍五入减少误差)
                x = int(round((event.x - self.bg_x) * self.bg_scale_x))
                y = int(round((event.y - self.bg_y) * self.bg_scale_y))

                # 限制坐标在图片范围内
                x = max(0, min(x, self.background_image.width - 1))
                y = max(0, min(y, self.background_image.height - 1))

                # 获取像素颜色
                rgb = self.background_image.getpixel((x, y))
                if isinstance(rgb, int):  # 灰度图像处理
                    rgb = (rgb, rgb, rgb)

                mode_text = "坐标获取" if self.current_mode == "coordinate" else "叠加图片"
                self.info_label.config(text=f"坐标: ({x}, {y}), RGB: {rgb} - 模式: {mode_text}")
            else:
                mode_text = "坐标获取" if self.current_mode == "coordinate" else "叠加图片"
                self.info_label.config(text=f"坐标: (0, 0) - 模式: {mode_text}")

    def clear_points(self):
        #####清除所有点#####
        self.points = []
        self.coord_list.delete(0, tk.END)
        self.canvas.delete("point")
        self.canvas.delete("point_text")

    def remove_selected_point(self):
        #####删除选中的坐标点#####
        selection = self.coord_list.curselection()
        if selection:
            index = selection[0]
            self.coord_list.delete(index)
            if index < len(self.points):
                del self.points[index]
            # 重新绘制所有点
            self.canvas.delete("point")
            self.canvas.delete("point_text")
            self.redraw_points()

    def save_data(self):
        #####保存所有数据(坐标点和叠加图片位置)#####
        if not self.background_image:
            messagebox.showinfo("提示", "没有数据可保存")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    # 保存背景图片信息
                    f.write(f"背景图片尺寸: {self.background_image.width} x {self.background_image.height}\n")
                    f.write("\n")

                    # 保存坐标点
                    f.write("坐标点(包含叠加图片位置):\n")
                    for point in self.points:
                        f.write(f"({point[0]}, {point[1]})\n")
                    f.write("\n")

                    # 保存叠加图片位置
                    f.write("叠加图片位置(左上角基准点):\n")
                    for img in self.draggable_images:
                        bg_x, bg_y = img.get_bg_coordinates()
                        f.write(f"{img.name}: ({bg_x}, {bg_y})\n")

                messagebox.showinfo("成功", f"数据已保存到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存文件时出错: {str(e)}")

                """
                txt文件格式例:
                背景图片尺寸:1920x1080

                坐标点(包含叠加图片位置):
                (-100,100)
                (200,400)
                (768,239)

                叠加图片位置(左上角基准点):
                n1(-100,100)
                n2(200,400)
                """

    def on_resize(self, event):
        #####窗口大小改变时重新显示图片#####
        if self.background_image:
            if self.current_mode == "overlay":
                self.display_background_image()
                self.bring_images_to_top()
                return

            self.display_background_image()


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCoordinatePicker(root)

    # 绑定窗口大小改变事件
    root.bind("<Configure>", app.on_resize)

    root.mainloop()
