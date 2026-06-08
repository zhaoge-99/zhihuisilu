
# 读取当前文件
with open(r'./调查问卷.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到Q4的HTML结构，将data-type="multiple"改为"single"
old_q4 = '<div class="question" data-q="4" data-type="multiple">'
new_q4 = '<div class="question" data-q="4" data-type="single">'

content = content.replace(old_q4, new_q4)

# 更新multipleQuestions列表，移除4
old_multiple = "const multipleQuestions = [4, 5, 7, 9, 10, 11, 12, 14];"
new_multiple = "const multipleQuestions = [5, 7, 9, 10, 11, 12, 14];"

content = content.replace(old_multiple, new_multiple)

# 更新singleQuestions列表，添加4
old_single = "const singleQuestions = [3, 6, 8, 13];"
new_single = "const singleQuestions = [3, 4, 6, 8, 13];"

content = content.replace(old_single, new_single)

# 更新中文翻译，去掉"可多选"
old_q4_title = '"q4":"4. 你的汉语水平（可多选）："'
new_q4_title = '"q4":"4. 你的汉语水平："'

content = content.replace(old_q4_title, new_q4_title)

# 更新英文翻译
old_en_q4 = '"q4":"4. Your Chinese proficiency (multiple choice):"'
new_en_q4 = '"q4":"4. Your Chinese proficiency:"'

content = content.replace(old_en_q4, new_en_q4)

# 保存文件
with open(r'./调查问卷.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Q4已改为单选！")
print("📄 文件已保存")
