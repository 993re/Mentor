import flet as ft

# 知识数据库：键=知识名称，值=对应的前置知识列表
def fuzzy_search(input_name, base):
    """模糊搜索：查找包含输入关键词的知识"""
    match_list = []
    for name in base.keys():
        if input_name.lower() in name.lower():
            match_list.append(name)
    return match_list

def show_result(page: ft.Page, knowledge_list, base):
    """MarkDown格式输出结果, more number of # means more earlier prerequisites"""
    if not knowledge_list:
        raise ValueError("未找到匹配的知识，请更换关键词重试！")
        
    # 遍历所有匹配到的知识
    for know in knowledge_list:
        # 第一行：知识名称
        page.add(ft.Text(know))
        
        # 下面每行输出 #前置知识
        for pre in base[know]:
            page.add(ft.Text(f"# {pre}"))
    
    page.update()
        
        
def searcher(page: ft.Page, input, base):
    return show_result(page, fuzzy_search(input, base), base)

def main():
    print("===== 知识前置学习查询系统 =====")
    user_input = input("请输入你想学习的知识名称：")
    matched = fuzzy_search(user_input, knowledge_base)
    show_result(matched, knowledge_base)

if __name__ == "__main__":
    knowledge_base = {
    "Python编程": ["计算机基础", "英语基础"],
    "机器学习": ["Python编程", "线性代数", "概率论"],
    
    "深度学习": ["机器学习", "微积分", "Python编程"],
    "Java开发": ["计算机基础", "面向对象思想"],
    "数据结构": ["Python编程/Java开发", "离散数学"],
    "算法": ["数据结构", "数学逻辑"],
    "MySQL数据库": ["计算机基础", "SQL语法"],
    "网络原理": ["计算机基础"],
    "线性代数": ["高中数学"],
    "微积分": ["高中数学"],
    "概率论": ["高中数学"],
    "离散数学": ["高中数学"]
}
    main()