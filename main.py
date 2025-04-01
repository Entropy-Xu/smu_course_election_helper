import json
import threading
import time
import tkinter as tk
from tkinter import ttk
import tools
from PIL import Image, ImageTk
import time
import json
import os
from datetime import datetime

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SMU抢课")
        self.create_widgets()
        self.session = None
        self.semester_id_map = {}  # 用于存储选项文本到ID的映射
        self.semester_id = None
        self.profileid = None
        self.lesson_id = None
        self.running_threads = []  # 存储所有运行中的线程
        self.stop_flag = False  # 控制线程停止的标志
        
        # 创建日志目录
        self.log_dir = "logs"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # 初始化日志文件名
        self.log_file = os.path.join(self.log_dir, f"course_election_{datetime.now().strftime('%Y%m%d')}.log")
        
        # 记录启动日志
        self.write_log("程序启动")

    def write_log(self, message):
        """写入日志到文件"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            print(f"写入日志出错: {e}")

    def create_widgets(self):
        # 设置组件之间的间隔
        padx_value = 10
        pady_value = 5

        # 第一行：用户名输入区
        username_label = ttk.Label(self, text="学号")
        vcmd = (self.register(self.only_numeric_input), '%P')
        self.username_entry = ttk.Entry(self, validate="key", validatecommand=vcmd)
        
        # 第二行：密码输入区
        password_label = ttk.Label(self, text="密码")
        self.password_entry = ttk.Entry(self, show="*")
        
        # 第三行：验证码输入区
        captcha_label = ttk.Label(self, text="验证码")
        self.captcha_entry = ttk.Entry(self, validate="key", validatecommand=vcmd)
        self.captcha_image_label = ttk.Label(self, text="登录前请获取验证码")
        
        # 登录和刷新按钮
        login_button = ttk.Button(self, text="登录", command=self.login)
        refresh_button = ttk.Button(self, text="刷新验证码\n或重新登陆", command=self.set_captcha_pic)
        
        # 登录信息显示文本框
        self.info_text = ttk.Label(self, text="请先登录您的账号")
        
        # 左侧设置区域：profileid、lessonid、间隔时间输入框
        profileid_label = ttk.Label(self, text="Profileid")
        self.profileid_entry = ttk.Entry(self, validate="key", validatecommand=vcmd)
        lessonid_label = ttk.Label(self, text="Lessonid")
        self.lessonid_entry = ttk.Entry(self, validate="key", validatecommand=vcmd)
        interval_label = ttk.Label(self, text="间隔秒数")
        self.interval_entry = ttk.Entry(self, validate="key", validatecommand=vcmd)
        self.interval_entry.insert(0, "1")
        
        # 右侧：学期选择和课程搜索
        semester_label = ttk.Label(self, text="学期")
        self.semester_combobox = ttk.Combobox(self, values=[])
        lesson_label = ttk.Label(self, text="课程名")
        self.lesson_entry = ttk.Entry(self)
        self.lesson_button = ttk.Button(self, text="搜索课程名", command=self.search)
        
        # 中间区域：课程搜索结果表格
        self.tree = ttk.Treeview(self, height=6)
        self.tree['columns'] = ('Lessonid', '课序号', '课程号', '课程名', '教师', '实际人数', '上限')
        
        # 格式设置
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("Lessonid", anchor=tk.CENTER, width=80)
        self.tree.column("课序号", anchor=tk.CENTER, width=80)
        self.tree.column("课程号", anchor=tk.CENTER, width=80)
        self.tree.column("课程名", anchor=tk.CENTER, width=120)
        self.tree.column("教师", anchor=tk.CENTER, width=80)
        self.tree.column("实际人数", anchor=tk.CENTER, width=70)
        self.tree.column("上限", anchor=tk.CENTER, width=50)
        
        # 创建表头
        self.tree.heading("#0", text="", anchor=tk.CENTER)
        self.tree.heading("Lessonid", text="Lessonid", anchor=tk.CENTER)
        self.tree.heading("课序号", text="课序号", anchor=tk.CENTER)
        self.tree.heading("课程号", text="课程号", anchor=tk.CENTER)
        self.tree.heading("课程名", text="课程名", anchor=tk.CENTER)
        self.tree.heading("教师", text="教师", anchor=tk.CENTER)
        self.tree.heading("实际人数", text="实际人数", anchor=tk.CENTER)
        self.tree.heading("上限", text="上限", anchor=tk.CENTER)
        
        # 为Treeview添加滚动条
        tree_scroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        # 操作按钮区域（添加到待抢列表、从待抢列表移除）
        add_to_queue_button = ttk.Button(self, text="添加到待抢列表", command=self.add_to_queue)
        remove_from_queue_button = ttk.Button(self, text="从待抢列表移除", command=self.remove_from_queue)
        
        # 底部区域：待抢列表
        queue_label = ttk.Label(self, text="待抢列表")
        self.queue_tree = ttk.Treeview(self, height=5)
        self.queue_tree['columns'] = ('Lessonid', '课程名', '教师')
        
        self.queue_tree.column("#0", width=0, stretch=tk.NO)
        self.queue_tree.column("Lessonid", anchor=tk.CENTER, width=100)
        self.queue_tree.column("课程名", anchor=tk.CENTER, width=150)
        self.queue_tree.column("教师", anchor=tk.CENTER, width=100)
        
        self.queue_tree.heading("#0", text="", anchor=tk.CENTER)
        self.queue_tree.heading("Lessonid", text="Lessonid", anchor=tk.CENTER)
        self.queue_tree.heading("课程名", text="课程名", anchor=tk.CENTER)
        self.queue_tree.heading("教师", text="教师", anchor=tk.CENTER)
        
        # 为待抢列表添加滚动条
        queue_scroll = ttk.Scrollbar(self, orient="vertical", command=self.queue_tree.yview)
        self.queue_tree.configure(yscrollcommand=queue_scroll.set)
        
        # 控制台内容输出文本框
        self.console_text = tk.Text(self, height=10, width=50)
        self.console_text.insert(tk.END, "控制台内容输出文本框")
        
        # 控制按钮（开始、结束）
        start_button = ttk.Button(self, text="开始", command=self.start)
        stop_button = ttk.Button(self, text="结束", command=self.stop)
        
        # ======= 布局 =======
        
        # 第一行：用户名区域
        username_label.grid(row=0, column=0, padx=padx_value, pady=pady_value, sticky='e')
        self.username_entry.grid(row=0, column=1, padx=padx_value, pady=pady_value, sticky='w')
        login_button.grid(row=0, column=2, padx=padx_value, pady=pady_value, columnspan=2)
        
        # 第二行：密码区域
        password_label.grid(row=1, column=0, padx=padx_value, pady=pady_value, sticky='e')
        self.password_entry.grid(row=1, column=1, padx=padx_value, pady=pady_value, sticky='w')
        self.captcha_image_label.grid(row=1, column=2, padx=padx_value, pady=pady_value, rowspan=2, columnspan=2)
        
        # 第三行：验证码区域
        captcha_label.grid(row=2, column=0, padx=padx_value, pady=pady_value, sticky='e')
        self.captcha_entry.grid(row=2, column=1, padx=padx_value, pady=pady_value, sticky='w')
        
        # 第四行：刷新和登录信息
        refresh_button.grid(row=3, column=0, padx=padx_value, pady=pady_value)
        self.info_text.grid(row=3, column=1, columnspan=3, padx=padx_value, pady=pady_value, sticky='w')
        
        # 第五行：Profile和学期选择
        profileid_label.grid(row=4, column=0, padx=padx_value, pady=pady_value, sticky='e')
        self.profileid_entry.grid(row=4, column=1, padx=padx_value, pady=pady_value, sticky='w')
        semester_label.grid(row=4, column=2, padx=padx_value, pady=pady_value, sticky='e')
        self.semester_combobox.grid(row=4, column=3, padx=padx_value, pady=pady_value, sticky='w')
        
        # 第六行：Lessonid和课程名
        lessonid_label.grid(row=5, column=0, padx=padx_value, pady=pady_value, sticky='e')
        self.lessonid_entry.grid(row=5, column=1, padx=padx_value, pady=pady_value, sticky='w')
        lesson_label.grid(row=5, column=2, padx=padx_value, pady=pady_value, sticky='e')
        self.lesson_entry.grid(row=5, column=3, padx=padx_value, pady=pady_value, sticky='w')
        
        # 第七行：间隔时间和搜索按钮
        interval_label.grid(row=6, column=0, padx=padx_value, pady=pady_value, sticky='e')
        self.interval_entry.grid(row=6, column=1, padx=padx_value, pady=pady_value, sticky='w')
        self.lesson_button.grid(row=6, column=3, padx=padx_value, pady=pady_value)
        
        # 第八行：课程搜索结果表格
        self.tree.grid(row=7, column=0, padx=padx_value, pady=pady_value, columnspan=4, sticky='nsew')
        tree_scroll.grid(row=7, column=4, pady=pady_value, sticky='ns')
        
        # 第九行：添加/移除待抢列表按钮
        add_to_queue_button.grid(row=8, column=1, padx=padx_value, pady=pady_value)
        remove_from_queue_button.grid(row=8, column=2, padx=padx_value, pady=pady_value)
        
        # 第十行：待抢列表标签
        queue_label.grid(row=9, column=0, padx=padx_value, pady=pady_value, sticky='w')
        
        # 第十一行：待抢列表
        self.queue_tree.grid(row=10, column=0, padx=padx_value, pady=pady_value, columnspan=4, sticky='nsew')
        queue_scroll.grid(row=10, column=4, pady=pady_value, sticky='ns')
        
        # 第十二行：控制台
        self.console_text.grid(row=11, column=0, padx=padx_value, pady=pady_value, columnspan=4, sticky='nsew')
        
        # 第十三行：控制按钮
        start_button.grid(row=12, column=1, padx=padx_value, pady=pady_value)
        stop_button.grid(row=12, column=2, padx=padx_value, pady=pady_value)
        
        # 绑定事件
        self.semester_combobox.bind("<<ComboboxSelected>>", self.on_combobox_select)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def only_numeric_input(self,P):
        # 如果输入为空或者为数字，则验证通过
        if P.isdigit() or P == "":
            return True
        else:
            return False

    def set_captcha_pic(self):
        # 获取图片
        self.session, self.execution = tools.get_captcha()
        # 打开图片
        captcha_image = Image.open("captcha.png")
        # 缩放图片到新尺寸，例如100x50
        new_size = (108, 50)
        resized_captcha = captcha_image.resize(new_size)
        # 将缩放后的图片转换为PhotoImage
        captcha_photo = ImageTk.PhotoImage(resized_captcha)
        # 保存对PhotoImage对象的引用，防止被垃圾回收
        self.captcha_image = captcha_photo
        # 更新标签的图片
        self.captcha_image_label.config(image=captcha_photo)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        validateCode = self.captcha_entry.get()

        if self.session and username and password and self.execution and validateCode is not None:
            name_and_id = tools.login(self.session, username, password, validateCode, self.execution)
            if name_and_id:
                self.info_text.config(text=f"登陆成功 {name_and_id}", foreground="green")

                self.semester = tools.get_semester(self.session)
                self.update_semester_options(self.semester)

                self.profileid = tools.get_profileid(self.session)
                if self.profileid:
                    self.profileid_entry.delete(0, tk.END)  # 删除profileid当前内容
                    self.profileid_entry.insert(0, self.profileid)  # 插入profileid
                    self.info_text.config(text=f"登陆成功 {name_and_id} 已获取到profileid={self.profileid}", foreground="green")
                else:
                    self.info_text.config(text=f"登陆成功 {name_and_id} 暂未获取到profileid",foreground="green")

            else:
                self.info_text.config(text="登陆失败 请刷新验证码后重试", foreground="red")
        else:
            self.info_text.config(text="登陆失败 您还未填写学号、密码、验证码", foreground="red")

    def update_semester_options(self, json_data):
        semester_options = []
        self.semester_id_map.clear()  # 清除旧的映射
        # 从json_data构建选项列表
        json_data = json.loads(json_data)
        for item in json_data:
            option_text = f"{item['schoolYear']} {item['name']}"
            semester_options.append(option_text)
            self.semester_id_map[option_text] = item['id']

        self.semester_combobox['values'] = semester_options
        if semester_options:
            self.semester_combobox.current(0)

    def on_combobox_select(self, event):
        selected_option = self.semester_combobox.get()
        self.semester_id = self.semester_id_map.get(selected_option)
        print(f"选中的学期ID: {self.semester_id}")

    def search(self):
        lesson_name = self.lesson_entry.get()
        if lesson_name and self.semester_id:
            lesson_data = tools.search_lesson(self.session, self.semester_id, lesson_name)
            self.clear_treeview()
            for item in lesson_data:
                self.tree.insert('', 'end', values=item)

    # 清除 Treeview 中的所有数据
    def clear_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def on_tree_select(self,event):
        # 获取选中的行ID
        selected_id = self.tree.selection()

        # 遍历所有选中的项（本例中假设只能选中一个）
        for sid in selected_id:
            item = self.tree.item(sid)
            self.lesson_id = item['values'][0]
            print(f"选中的Lessonid: {self.lesson_id}")
            self.lessonid_entry.delete(0, tk.END)  # 删除Lessonid当前内容
            self.lessonid_entry.insert(0, self.lesson_id)  # 插入Lessonid
    
    def add_to_queue(self):
        # 获取当前选中的课程
        selected_id = self.tree.selection()
        if not selected_id:
            return
            
        for sid in selected_id:
            item = self.tree.item(sid)
            lesson_id = item['values'][0]
            course_name = item['values'][3]
            teacher = item['values'][4]
            
            # 检查是否已存在于待抢列表中
            for qid in self.queue_tree.get_children():
                if self.queue_tree.item(qid)['values'][0] == lesson_id:
                    return  # 已存在，不重复添加
                    
            # 添加到待抢列表
            self.queue_tree.insert('', 'end', values=(lesson_id, course_name, teacher))
            
    def remove_from_queue(self):
        # 从待抢列表中移除选中项
        selected_id = self.queue_tree.selection()
        for sid in selected_id:
            self.queue_tree.delete(sid)

    def start(self):
        self.wait_time = self.interval_entry.get()
        self.profileid = self.profileid_entry.get()
        
        # 检查参数是否齐全
        if not self.session or not self.profileid or not self.wait_time:
            self.console_text.insert(tk.END, "\n参数不齐全，请确保已登录并填写Profileid和间隔秒数")
            return
            
        try:
            self.wait_time = float(self.wait_time)
        except ValueError:
            self.console_text.insert(tk.END, "\n间隔秒数格式错误，请输入有效的数字")
            return
            
        # 重置停止标志
        self.stop_flag = False
        
        # 获取待抢列表中的所有课程
        queue_items = self.queue_tree.get_children()
        
        if not queue_items:
            # 如果待抢列表为空，使用输入框中的lessonid
            lesson_id = self.lessonid_entry.get()
            if lesson_id:
                self.start_single_thread(lesson_id)
            else:
                self.console_text.insert(tk.END, "\n请输入Lessonid或添加课程到待抢列表")
        else:
            # 为待抢列表中的每个课程创建一个线程
            for item_id in queue_items:
                item = self.queue_tree.item(item_id)
                lesson_id = item['values'][0]
                self.start_single_thread(lesson_id)
    
    def start_single_thread(self, lesson_id):
        # 启动一个后台线程执行抢课操作
        thread = threading.Thread(
            target=self.perform_concurrent_operations, 
            args=(self.session, self.profileid, lesson_id, self.wait_time),
            daemon=True
        )
        thread.start()
        self.running_threads.append(thread)
        self.console_text.insert(tk.END, f"\n开始抢课 Lessonid: {lesson_id}")
    
    def stop(self):
        # 设置停止标志为True，告诉所有线程停止
        self.stop_flag = True
        message = "已发送停止信号，等待线程结束..."
        self.console_text.insert(tk.END, f"\n{message}")
        self.write_log(message)
        self.console_text.see(tk.END)
        
        # 清空线程列表
        self.running_threads = []

    def perform_concurrent_operations(self, session, profileId, lessonid, wait_time):
        wait_time_ms = int(wait_time * 1000)  # 转换为毫秒
        
        # 获取sessiontime
        self.sessiontime = tools.get_sessiontime(session, profileId)
        if not self.sessiontime:
            message = f"Lessonid:{lessonid} 无法获取sessiontime，请重新登录"
            self.console_text.insert(tk.END, f"\n{message}")
            self.write_log(message)
            return
        
        # 将结果显示在控制台文本框中
        message = f"开始抢课 {lessonid} sessiontime={self.sessiontime}"
        self.console_text.insert(tk.END, f"\n{message}")
        self.write_log(message)
        self.console_text.see(tk.END)  # 滚动到文本框底部
        
        count = 0
        consecutive_errors = 0  # 连续错误计数
        max_consecutive_errors = 5  # 最大连续错误次数
        
        while not self.stop_flag:  # 检查停止标志
            if consecutive_errors >= max_consecutive_errors:
                message = f"Lessonid:{lessonid} 连续出错{max_consecutive_errors}次，暂停该课程抢课"
                self.console_text.insert(tk.END, f"\n{message}")
                self.write_log(message)
                self.console_text.see(tk.END)
                break
            
            count += 1
            result = tools.elect(session, profileId, self.sessiontime, lessonid)
            
            # 在UI线程中更新文本框
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            message = f"[{current_time}] Lessonid:{lessonid} 第{count}次抢课 结果: {result}"
            self.console_text.insert(tk.END, f"\n{message}")
            self.console_text.see(tk.END)  # 滚动到文本框底部
            
            # 如果抢课成功包含"成功"，则退出循环
            if "成功" in result:
                message = f"[{current_time}] Lessonid:{lessonid} 抢课成功！停止抢课"
                self.console_text.insert(tk.END, f"\n{message}")
                self.write_log(message)
                self.console_text.see(tk.END)
                break
            
            # 检查session是否过期
            if "会话已经失效" in result:
                # 重新获取sessiontime
                new_sessiontime = tools.get_sessiontime(session, profileId)
                if new_sessiontime:
                    self.sessiontime = new_sessiontime
                    message = f"[{current_time}] Lessonid:{lessonid} 会话已失效，已更新sessiontime={self.sessiontime}"
                    self.console_text.insert(tk.END, f"\n{message}")
                    self.write_log(message)
                    consecutive_errors = 0  # 重置错误计数
                else:
                    consecutive_errors += 1
                    message = f"[{current_time}] Lessonid:{lessonid} 无法获取新的sessiontime，尝试次数: {consecutive_errors}"
                    self.console_text.insert(tk.END, f"\n{message}")
                    self.write_log(message)
            elif "错误" in result or "超时" in result or "连接错误" in result:
                consecutive_errors += 1
                message = f"[{current_time}] Lessonid:{lessonid} 发生错误，尝试次数: {consecutive_errors}"
                self.console_text.insert(tk.END, f"\n{message}")
                if consecutive_errors >= 3:  # 只在错误较严重时记录日志
                    self.write_log(message)
            else:
                consecutive_errors = 0  # 重置错误计数
                
            self.console_text.see(tk.END)
            time.sleep(wait_time)  # 使用秒为单位的等待时间


# 运行程序
if __name__ == "__main__":
    app = Application()
    
    # 添加窗口关闭事件处理
    def on_closing():
        if app.running_threads:
            app.stop()
        app.write_log("程序退出")
        app.destroy()
        
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()
