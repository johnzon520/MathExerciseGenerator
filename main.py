import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import time
from threading import Thread

class MathExerciseGenerator:
    def __init__(self):
        """初始化题库和用户设置"""
        self.count = 80
        self.max_number = 20
        self.include_add_without_carry = True
        self.include_add_with_carry = True
        self.include_sub_without_borrow = True
        self.include_sub_with_borrow = True
        self.random_answer_position = False
        self.current_exercises = []
        self.font_name = self.register_fonts()
        self.exercise_set = set()  # 用于存储已生成的题目，避免重复

    def register_fonts(self):
        """注册中文字体"""
        try:
            font_paths = {
                'SimHei': 'simhei.ttf',
                'Microsoft YaHei': 'msyh.ttf',
                'WenQuanYi Micro Hei': 'wqy-microhei.ttc'
            }
            for name, path in font_paths.items():
                try:
                    pdfmetrics.registerFont(TTFont(name, path))
                    return name
                except:
                    continue
            pdfmetrics.registerFont(TTFont('SimHei', 'SimHei'))
            return 'SimHei'
        except:
            return 'Helvetica'

    def set_configuration(self, count, max_number, add_without_carry, add_with_carry, 
                         sub_without_borrow, sub_with_borrow, random_answer_position=False):
        """验证并设置配置"""
        if count < 1:
            raise ValueError("题目数量必须大于0")
        if max_number not in (20, 100):
            raise ValueError("请选择20或100以内的题目")
        if not any([add_without_carry, add_with_carry, sub_without_borrow, sub_with_borrow]):
            raise ValueError("至少选择一种题型")
        self.count = count
        self.max_number = max_number
        self.include_add_without_carry = add_without_carry
        self.include_add_with_carry = add_with_carry
        self.include_sub_without_borrow = sub_without_borrow
        self.include_sub_with_borrow = sub_with_borrow
        self.random_answer_position = random_answer_position
        self.exercise_set = set()  # 重置题目集合

    def generate_add_without_carry(self):
        """生成不进位加法题"""
        for _ in range(100):  # 最多尝试100次
            if self.max_number == 20:
                num1 = random.randint(1, 18)
                max_num2 = min(9 - (num1 % 10), 20 - num1)
                if max_num2 < 1:
                    continue
                num2 = random.randint(1, max_num2)
                # 再次检查确保不进位
                if (num1 % 10) + (num2 % 10) >= 10:
                    continue
            else:
                # 100以内不进位加法，确保都是两位数
                num1 = random.randint(10, 99)
                # 十位数相加不超过9
                max_tens = min(9 - (num1 // 10), 9)
                if max_tens < 1:
                    continue
                tens = random.randint(1, max_tens)
                # 个位数相加不超过9
                max_units = min(9 - (num1 % 10), 9)
                if max_units < 0:
                    continue
                units = random.randint(0, max_units)
                num2 = tens * 10 + units
                # 再次检查确保不进位
                if (num1 % 10) + (num2 % 10) >= 10 or (num1 // 10) + (num2 // 10) >= 10:
                    continue
            
            equation = f"{num1}+{num2}"
            if equation not in self.exercise_set:
                self.exercise_set.add(equation)
                return self.format_equation(num1, "+", num2, num1 + num2)
        
        # 如果无法生成不进位题目，尝试生成进位题目
        return self.generate_add_with_carry()

    def generate_add_with_carry(self):
        """生成进位加法题"""
        for _ in range(100):
            if self.max_number == 20:
                num1 = random.randint(10, 18)
                min_num2 = max(1, 10 - (num1 % 10))
                max_num2 = min(9, 20 - num1)
                if min_num2 > max_num2:
                    continue
                num2 = random.randint(min_num2, max_num2)
                # 确保确实会进位
                if (num1 % 10) + (num2 % 10) < 10:
                    continue
            else:
                # 100以内进位加法，确保都是两位数
                num1 = random.randint(10, 99)
                # 确保个位数相加≥10
                min_units = max(0, 10 - (num1 % 10))
                max_units = 9
                if min_units > max_units:
                    continue
                units = random.randint(min_units, max_units)
                # 十位数可以任意，但第二个数也是两位数
                max_tens = min(9, (99 - num1 - units) // 10)
                if max_tens < 1:
                    continue
                tens = random.randint(1, max_tens)
                num2 = tens * 10 + units
                # 再次检查确保个位数相加会进位
                if (num1 % 10) + (num2 % 10) < 10:
                    continue
            
            equation = f"{num1}+{num2}"
            if equation not in self.exercise_set:
                self.exercise_set.add(equation)
                return self.format_equation(num1, "+", num2, num1 + num2)
        
        # 如果无法生成进位题目，尝试生成不进位题目
        return self.generate_add_without_carry()

    def generate_sub_without_borrow(self):
        """生成不借位减法题"""
        for _ in range(100):
            if self.max_number == 20:
                num1 = random.randint(10, 20)
                max_num2 = min(num1 % 10, num1 - 1)
                if max_num2 < 1:
                    continue
                num2 = random.randint(1, max_num2)
                # 确保不借位
                if (num1 % 10) < (num2 % 10):
                    continue
            else:
                # 100以内不借位减法，确保都是两位数
                num1 = random.randint(10, 99)
                # 确保十位数不借位
                min_tens = 1
                max_tens = num1 // 10 - 1
                if max_tens < min_tens:
                    continue
                tens = random.randint(min_tens, max_tens)
                # 确保个位数不借位
                max_units = num1 % 10
                if max_units < 0:
                    continue
                units = random.randint(0, max_units)
                num2 = tens * 10 + units
                # 再次检查确保不借位
                if (num1 % 10) < (num2 % 10) or (num1 // 10) < (num2 // 10):
                    continue
            
            equation = f"{num1}-{num2}"
            if equation not in self.exercise_set:
                self.exercise_set.add(equation)
                return self.format_equation(num1, "-", num2, num1 - num2)
        
        # 如果无法生成不借位题目，尝试生成借位题目
        return self.generate_sub_with_borrow()

    def generate_sub_with_borrow(self):
        """生成借位减法题"""
        for _ in range(100):
            if self.max_number == 20:
                num1 = random.randint(11, 18)
                min_num2 = (num1 % 10) + 1
                max_num2 = num1 - 1
                if min_num2 > max_num2:
                    continue
                num2 = random.randint(min_num2, max_num2)
                # 确保确实会借位
                if (num1 % 10) >= (num2 % 10):
                    continue
            else:
                # 100以内借位减法，确保都是两位数
                num1 = random.randint(10, 99)
                # 确保被减数大于减数
                min_num2 = 10
                max_num2 = num1 - 1
                if min_num2 > max_num2:
                    continue
                num2 = random.randint(min_num2, max_num2)
                # 确保个位需要借位
                if (num1 % 10) >= (num2 % 10):
                    continue
            
            equation = f"{num1}-{num2}"
            if equation not in self.exercise_set:
                self.exercise_set.add(equation)
                return self.format_equation(num1, "-", num2, num1 - num2)
        
        # 如果无法生成借位题目，尝试生成不借位题目
        return self.generate_sub_without_borrow()

    def format_equation(self, num1, operator, num2, answer):
        """格式化算式，根据设置随机化得数位置"""
        if not self.random_answer_position:
            return f"{num1} {operator} {num2} ="
        
        # 随机选择得数位置（0: 第一个数位置, 1: 第二个数位置, 2: 得数位置）
        position = random.randint(0, 2)
        
        # 如果是减法且答案会是负数，就保持标准形式
        if operator == "-" and answer < 0:
            return f"{num1} {operator} {num2} ="
        
        if position == 0:  # 得数在第一个数位置
            # 确保=后面的数不超过范围且不是负数
            if (self.max_number == 20 and answer > 20) or (self.max_number == 100 and answer > 100) or answer < 0:
                return f"{num1} {operator} {num2} ="  # 如果会超范围或负数，就保持原样
            return f"(    ) {operator} {num2} = {answer}"
        elif position == 1:  # 得数在第二个数位置
            # 确保=后面的数不超过范围且不是负数
            if (self.max_number == 20 and answer > 20) or (self.max_number == 100 and answer > 100) or answer < 0:
                return f"{num1} {operator} {num2} ="  # 如果会超范围或负数，就保持原样
            return f"{num1} {operator} (    ) = {answer}"
        else:  # 得数在正常位置
            return f"{num1} {operator} {num2} =(    )"

    def generate_exercise(self):
        """生成练习题"""
        try:
            exercises = []
            generators = []
            if self.include_add_without_carry:
                generators.append(self.generate_add_without_carry)
            if self.include_add_with_carry:
                generators.append(self.generate_add_with_carry)
            if self.include_sub_without_borrow:
                generators.append(self.generate_sub_without_borrow)
            if self.include_sub_with_borrow:
                generators.append(self.generate_sub_with_borrow)

            if not generators:
                raise ValueError("至少选择一种题型")

            # 先清空题目集合
            self.exercise_set = set()

            per_type = max(1, self.count // len(generators))
            for generator in generators:
                count = 0
                while count < per_type:
                    try:
                        exercise = generator()
                        if exercise:
                            exercises.append(exercise)
                            count += 1
                    except:
                        break

            # 如果生成的题目不足，尝试用其他题型补充
            while len(exercises) < self.count and generators:
                generator = random.choice(generators)
                try:
                    exercise = generator()
                    if exercise:
                        exercises.append(exercise)
                except:
                    continue

            random.shuffle(exercises)
            self.current_exercises = exercises[:self.count]
            return self.current_exercises
        except Exception as e:
            raise ValueError(f"生成题目失败: {str(e)}")

    def generate_pdf(self, filename):
        """生成PDF文件（80题行间距12pt）"""
        try:
            c = canvas.Canvas(filename, pagesize=A4)
            width, height = A4
            margin = 35
            usable_width = width - 2 * margin
            usable_height = height - 2 * margin
            cols = 4
            col_width = usable_width / cols

            # 标题表格
            title_data = [["姓名：", "日期：", "得分：", "表现：☆☆☆☆☆"]]
            title_style = TableStyle([
                ('FONTNAME', (0,0), (-1,-1), self.font_name),
                ('FONTSIZE', (0,0), (-1,-1), 14),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ])
            title_table = Table(title_data, colWidths=[col_width]*cols)
            title_table.setStyle(title_style)
            title_height = 30

            # 题目表格
            table_data = []
            for i in range(0, len(self.current_exercises), cols):
                row = self.current_exercises[i:i+cols]
                row += [''] * (cols - len(row))
                table_data.append(row)
            
            is_80_questions = len(self.current_exercises) <= 80
            font_size = 14 if self.random_answer_position else 16
            exercise_style = TableStyle([
                ('FONTNAME', (0,0), (-1,-1), self.font_name),
                ('FONTSIZE', (0,0), (-1,-1), font_size),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 12 if is_80_questions else 8),
                ('TOPPADDING', (0,0), (-1,-1), 7),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ])
            t = Table(table_data, colWidths=[col_width]*cols)
            t.setStyle(exercise_style)

            # 定位绘制
            title_y = height - margin - 20
            title_table.wrapOn(c, usable_width, title_height)
            title_table.drawOn(c, margin, title_y - title_height)
            
            t.wrapOn(c, usable_width, usable_height - title_height - 20)
            exercise_y = title_y - title_height - 20 - t._height
            if exercise_y < margin:
                title_y = height - margin - t._height - 60
                exercise_y = title_y - title_height - 20
                title_table.drawOn(c, margin, title_y - title_height)
            t.drawOn(c, margin, exercise_y)
            
            c.save()
            return True
        except Exception as e:
            raise ValueError(f"生成PDF失败: {str(e)}")

class MathExerciseGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("小学加减法生成器")
        self.root.geometry("500x650")
        self.generator = MathExerciseGenerator()
        self.setup_ui()

    def setup_ui(self):
        """创建用户界面"""
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="小学加减法生成器", font=('Microsoft YaHei', 16, 'bold'))
        title_label.pack()
        ttk.Label(main_frame).pack()  # 空行作为间隔
        
        # 题目数量
        ttk.Label(main_frame, text="题目数量:").pack(anchor=tk.W)
        self.count_var = tk.IntVar(value=80)
        ttk.Radiobutton(main_frame, text="80题", variable=self.count_var, value=80).pack(anchor=tk.W)
        ttk.Radiobutton(main_frame, text="100题", variable=self.count_var, value=100).pack(anchor=tk.W)
        
        # 题目范围
        ttk.Label(main_frame).pack()  # 空行作为间隔
        ttk.Label(main_frame, text="题目范围:").pack(anchor=tk.W)
        self.range_var = tk.IntVar(value=20)
        ttk.Radiobutton(main_frame, text="20以内", variable=self.range_var, value=20).pack(anchor=tk.W)
        ttk.Radiobutton(main_frame, text="100以内", variable=self.range_var, value=100).pack(anchor=tk.W)
        
        # 题型选择
        ttk.Label(main_frame).pack()  # 空行作为间隔
        ttk.Label(main_frame, text="题型选择:").pack(anchor=tk.W)
        self.add1_var = tk.BooleanVar(value=True)
        self.add2_var = tk.BooleanVar(value=True)
        self.sub1_var = tk.BooleanVar(value=True)
        self.sub2_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="加法不进位", variable=self.add1_var).pack(anchor=tk.W)
        ttk.Checkbutton(main_frame, text="加法进位", variable=self.add2_var).pack(anchor=tk.W)
        ttk.Checkbutton(main_frame, text="减法不借位", variable=self.sub1_var).pack(anchor=tk.W)
        ttk.Checkbutton(main_frame, text="减法借位", variable=self.sub2_var).pack(anchor=tk.W)
        
        # 得数位置随机选项
        ttk.Label(main_frame).pack()  # 空行作为间隔
        ttk.Label(main_frame, text="得数位置:").pack(anchor=tk.W)
        self.random_pos_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(main_frame, text="随机得数位置(用括号表示)", variable=self.random_pos_var).pack(anchor=tk.W)
        
        # 生成按钮
        ttk.Label(main_frame).pack()  # 空行作为间隔
        ttk.Button(main_frame, text="生成练习题", command=self.start_generation).pack()
        
        # 状态标签
        ttk.Label(main_frame).pack()  # 空行作为间隔
        self.status_var = tk.StringVar()
        ttk.Label(main_frame, textvariable=self.status_var, foreground='blue').pack()

    def start_generation(self):
        """启动生成过程"""
        self.status_var.set("准备生成题目...")
        Thread(target=self.generate_exercises, daemon=True).start()

    def generate_exercises(self):
        """生成练习题"""
        try:
            progress = tk.Toplevel(self.root)
            progress.title("正在生成")
            progress.geometry("300x150")
            ttk.Label(progress, text="正在生成题目，请稍候...").pack(pady=20)
            pb = ttk.Progressbar(progress, mode='indeterminate')
            pb.pack(fill=tk.X, padx=20)
            pb.start()
            
            self.generator.set_configuration(
                count=self.count_var.get(),
                max_number=self.range_var.get(),
                add_without_carry=self.add1_var.get(),
                add_with_carry=self.add2_var.get(),
                sub_without_borrow=self.sub1_var.get(),
                sub_with_borrow=self.sub2_var.get(),
                random_answer_position=self.random_pos_var.get()
            )
            
            exercises = self.generator.generate_exercise()
            self.status_var.set(f"成功生成 {len(exercises)} 道题目")
            
            default_name = f"{self.range_var.get()}以内加减法_{self.count_var.get()}题.pdf"
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                initialfile=default_name,
                filetypes=[("PDF文件", "*.pdf")]
            )
            
            if filename:
                success = self.generator.generate_pdf(filename)
                if success:
                    self.status_var.set(f"已保存到: {filename}")
            
            progress.destroy()
        except Exception as e:
            messagebox.showerror("错误", str(e))
            self.status_var.set("生成失败")

if __name__ == "__main__":
    root = tk.Tk()
    try:
        style = ttk.Style()
        style.theme_use('clam')
        font = ('Microsoft YaHei', 12)
        style.configure('.', font=font)
        app = MathExerciseGUI(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("启动错误", f"程序无法启动: {str(e)}")    
