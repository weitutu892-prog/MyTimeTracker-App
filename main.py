import flet as ft
import datetime
import json
import os

DATA_FILE = "time_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "records" in data and "current" in data:
                    return data
        except:
            pass
    return {"records": [], "current": None}

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"数据保存失败: {e}")

def main(page: ft.Page):
    # 💻 允许自由拉伸窗口，提供更广阔的视觉比例
    page.window_width = 800
    page.window_height = 850
    page.title = "⏳ 个人时间轴与感悟 App"
    page.padding = 25  # 增加页面内边距
    page.scroll = "auto" # 恢复大页面自然滚动

    user_data = load_data()

    # --- UI 组件定义 ---
    timeline_container = ft.Column(spacing=12, scroll="auto")
    current_status_text = ft.Text(value="⏸️ 当前没有正在进行的活动", size=15, color="#757575", weight="bold")
    summary_text = ft.Text(value="暂无周期总结数据，开始记录你的一天吧！", size=13, color="#424242")

    msg_snack = ft.SnackBar(content=ft.Text(value=""))
    page.snack_bar = msg_snack

    # --- 核心数据结算逻辑 ---
    def execute_activity_toggle(activity_name, from_submit=False):
        now = datetime.datetime.now()
        now_time = now.strftime("%H:%M")
        now_date = now.strftime("%m-%d") 
        current_feeling = feeling_input.value.strip()

        if user_data["current"]:
            prev_activity = user_data["current"]
            user_data["records"].append({
                "activity": prev_activity["name"],
                "start": prev_activity["start"],
                "end": now_time,
                "date": now_date,
                "feeling": current_feeling
            })
            
            if from_submit or prev_activity["name"] == activity_name:
                user_data["current"] = None
                msg_snack.content.value = f"✅ 已成功保存感悟并结算：{prev_activity['name']}"
            else:
                user_data["current"] = {"name": activity_name, "start": now_time}
                msg_snack.content.value = f"🔄 已结算上一项，开始记录：{activity_name}"
        else:
            if from_submit:
                msg_snack.content.value = "💡 提示：当前没有正在进行的活动"
            else:
                user_data["current"] = {"name": activity_name, "start": now_time}
                msg_snack.content.value = f"▶️ 开始记录：{activity_name}"
        
        msg_snack.open = True
        feeling_input.value = "" 
        save_data(user_data)
        refresh_ui()

    def click_code(e): execute_activity_toggle("代码", False)
    def click_study(e): execute_activity_toggle("学习", False)
    def click_sport(e): execute_activity_toggle("运动", False)
    def click_rest(e): execute_activity_toggle("休息", False)

    def on_feeling_submit(e):
        if user_data["current"]:
            execute_activity_toggle(user_data["current"]["name"], True)
        else:
            msg_snack.content.value = "💡 提示：当前没有正在进行的活动"
            msg_snack.open = True
            page.update()

    def clear_all_data(e):
        user_data["records"] = []
        user_data["current"] = None
        save_data(user_data)
        refresh_ui()
        msg_snack.content.value = "历史数据已清空"
        msg_snack.open = True
        page.update()

    # 去掉死宽度，在大分辨率下更舒展
    feeling_input = ft.TextField(
        label="写下当下的感受，直接敲「回车键」即可保存并结算...",
        text_size=14,
        multiline=False, 
        on_submit=on_feeling_submit,
        border_color="#2196F3",
        expand=True  # 自动填满横向空间
    )

    def refresh_ui():
        timeline_container.controls.clear()
        
        if user_data.get("current"):
            curr = user_data["current"]
            current_status_text.value = f"▶️ 正在进行：{curr['name']} (自 {curr['start']} 开始)"
            current_status_text.color = "#2196F3"  
        else:
            current_status_text.value = "⏸️ 当前没有正在进行的活动"
            current_status_text.color = "#757575"  

        records = user_data.get("records", [])
        if not records:
            timeline_container.controls.append(
                ft.Text(value="🌱 还没有历史足迹，点击上方按钮开始记录吧~", size=13, color="#9E9E9E", italic=True)
            )
        else:
            for record in reversed(records):
                rec_date = record.get("date", "")
                rec_feeling = record.get("feeling", "").strip()
                
                row_content = [
                    ft.Text(value=" • ", size=20, color="#FF9800", weight="bold"),
                    ft.Text(value=f"{record['activity']}", size=15, weight="bold", color="black"),
                    ft.Text(value=f" ({record['start']}-{record['end']})", size=12, color="#9E9E9E")
                ]
                if rec_feeling:
                    row_content.append(ft.Text(value=f" 💬 {rec_feeling}", size=13, italic=True, color="#546E7A"))
                
                timeline_container.controls.append(
                    ft.Container(
                        content=ft.Row(controls=row_content, wrap=True),
                        padding=12,
                        border_radius=8,
                        bgcolor="#F5F5F5"
                    )
                )

        if not records:
            summary_text.value = "🌱 暂无总结。多记录一些活动，看板会自动生成哦！"
        else:
            recent_records = records[-5:]
            summary_lines = ["📋 【近期心路历程总结】"]
            for r in reversed(recent_records):
                summary_lines.append(f"• {r['start']}-{r['end']}【{r['activity']}】{r.get('feeling','')}")
            summary_text.value = "\n".join(summary_lines)
            
        page.update()

    # --- 布局定义 ---
    title_row = ft.Row(
        controls=[
            ft.Text(value="⏳ 我的时间轴", size=24, weight="bold", color="black"),
            ft.Container(
                content=ft.Text(value="清空数据", color="red", weight="bold", size=13),
                on_click=clear_all_data,
                padding=8,
                border_radius=5,
                bgcolor="#FFEBEE"
            )
        ], 
        alignment="spaceBetween"
    )

    # ✨ 绝对兼容修复：直接将 padding 设为整数 12，避开任何 ft.padding 模块调用
    def build_responsive_button(text, emoji, bg_color, click_fn):
        return ft.Container(
            content=ft.Row(
                controls=[ft.Text(value=emoji, size=16), ft.Text(value=text, weight="bold", color="black", size=14)], 
                alignment="center",
                spacing=6
            ),
            padding=12,       # 四周全部填充 12 像素，没有任何高级属性依赖
            bgcolor=bg_color, 
            border_radius=8,
            on_click=click_fn
        )

    btn_code = build_responsive_button("代码", "💻", "#E3F2FD", click_code)
    btn_study = build_responsive_button("学习", "📚", "#EDE7F6", click_study)
    btn_sport = build_responsive_button("运动", "🏃", "#E8F5E9", click_sport)
    btn_rest = build_responsive_button("休息", "☕", "#FFF3E0", click_rest)

    # 面板宽度自适应扩展
    summary_card = ft.Container(
        content=ft.Column(controls=[
            ft.Text(value="📊 周期回顾看板", size=16, weight="bold", color="#1E88E5"),
            ft.Divider(height=10, color="#E0E0E0"),
            summary_text
        ]),
        padding=16,
        border_radius=12,
        bgcolor="#E8F5E9"
    )

    # --- 页面响应式装载 ---
    page.add(
        title_row,
        ft.Container(height=10),
        ft.Row(controls=[btn_code, btn_study, btn_sport, btn_rest], alignment="start", spacing=12), 
        ft.Container(height=10),
        ft.Row(controls=[feeling_input]), # 让输入框弹性铺满          
        ft.Container(height=10),
        current_status_text,
        ft.Container(height=10),
        ft.Text(value="今日足迹：", size=15, weight="bold", color="black"),
        timeline_container,
        ft.Container(height=15),
        summary_card            
    )

    refresh_ui()

if __name__ == "__main__":
    ft.run(main)