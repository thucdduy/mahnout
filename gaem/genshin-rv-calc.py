import itertools
from tabulate import tabulate

# Định nghĩa các giá trị rolls cho từng substat
substat_rolls = {
    "CRIT DMG (%)": [5.44, 6.22, 6.99, 7.77],
    "CRIT Rate (%)": [2.72, 3.11, 3.50, 3.89],
    "Energy Recharge (%)": [4.53, 5.18, 5.83, 6.48],
    "Elemental Mastery": [16.32, 18.65, 20.98, 23.31],
    "DEF (%)": [5.10, 5.83, 6.56, 7.29],
    "ATK (%)": [4.08, 4.66, 5.25, 5.83],
    "HP (%)": [4.08, 4.66, 5.25, 5.83],
    "DEF": [16.20, 18.52, 20.83, 23.15],
    "ATK": [13.62, 15.56, 17.51, 19.45],
    "HP": [209.13, 239.00, 268.88, 298.75]
}

# Danh sách substat để chọn (đã đảo ngược)
substat_list = list(substat_rolls.keys())

# Ánh xạ giá trị roll đến phần trăm
roll_value_mapping = {
    100: 3,  # Index trong danh sách rolls (100% = giá trị cao nhất)
    90: 2,
    80: 1,
    70: 0
}

def get_roll_percentage(value, rolls):
    """Tìm phần trăm Roll Value dựa trên giá trị roll."""
    for percentage, index in roll_value_mapping.items():
        if abs(value - rolls[index]) < 0.01:
            return percentage
    return 0

def find_roll_combination(substat_type, total_value):
    """Tìm tổ hợp rolls gần nhất với tổng giá trị nhập."""
    rolls = substat_rolls[substat_type]
    min_rolls = 1
    max_rolls = 5
    
    best_combination = None
    best_diff = float('inf')
    best_num_rolls = 0
    
    for num_rolls in range(min_rolls, max_rolls + 1):
        for combination in itertools.product(rolls, repeat=num_rolls):
            combo_sum = sum(combination)
            diff = abs(combo_sum - total_value)
            if diff < best_diff:
                best_diff = diff
                best_combination = combination
                best_num_rolls = num_rolls
                if diff < 0.01:
                    break
    
    return best_combination, best_num_rolls

def main():
    print("=== Artifact Roll Value Calculator ===")
    
    # Nhập số lượng substat
    while True:
        try:
            num_substats = int(input("Nhập số lượng substat (1 đến 4): "))
            if num_substats < 1 or num_substats > 4:
                print("Số lượng substat phải từ 1 đến 4.")
                continue
            break
        except ValueError:
            print("Vui lòng nhập số nguyên.")
    
    total_roll_value = 0.0
    substat_data = []
    crit_rate = 0.0
    crit_dmg = 0.0
    
    # Hiển thị danh sách substat (đã đảo ngược)
    print("\nDanh sách substat:")
    for i, substat in enumerate(substat_list, 1):
        print(f"{i}. {substat}")
    
    # Nhập substat bằng số liên tục
    while True:
        try:
            substat_input = input(f"\nChọn {num_substats} substat bằng số (1-{len(substat_list)}), cách nhau bằng khoảng trắng: ")
            substat_choices = [int(x) - 1 for x in substat_input.split()]
            if len(substat_choices) != num_substats:
                print(f"Vui lòng nhập đúng {num_substats} số.")
                continue
            if any(choice < 0 or choice >= len(substat_list) for choice in substat_choices):
                print("Lựa chọn không hợp lệ.")
                continue
            break
        except ValueError:
            print("Dữ liệu không hợp lệ. Vui lòng nhập số nguyên cách nhau bằng khoảng trắng.")
    
    # Nhập giá trị tổng cho các substat
    total_values = []
    for i, choice in enumerate(substat_choices, 1):
        substat_type = substat_list[choice]
        while True:
            try:
                value = float(input(f"Nhập giá trị tổng cho {substat_type}: "))
                total_values.append(value)
                break
            except ValueError:
                print("Vui lòng nhập số.")
    
    # Tính toán Roll Value và Crit Value
    for i, (choice, total_value) in enumerate(zip(substat_choices, total_values)):
        substat_type = substat_list[choice]
        rolls, num_rolls = find_roll_combination(substat_type, total_value)
        
        # Tạo chuỗi debug và tính Roll Value
        debug_str = ""
        substat_roll_value = 0.0
        for j, value in enumerate(rolls, 1):
            percentage = get_roll_percentage(value, substat_rolls[substat_type])
            roll_value = percentage / 100
            substat_roll_value += roll_value
            debug_str += f"{value:.2f} ({percentage}%)"
            if j < num_rolls:
                debug_str += " + "
        
        roll_value_percent = substat_roll_value * 100
        total_roll_value += substat_roll_value
        
        # Tính Crit Value cho substat này
        substat_crit_value = 0.0
        if substat_type == "CRIT Rate (%)":
            crit_rate = total_value
            substat_crit_value = 2 * total_value
        elif substat_type == "CRIT DMG (%)":
            crit_dmg = total_value
            substat_crit_value = total_value
        
        # Thêm vào bảng summary với định dạng CV/RV
        cv_rv_str = f"{substat_crit_value:.0f}%/{roll_value_percent:.0f}%"
        substat_data.append([i + 1, substat_type, total_value, num_rolls, debug_str, cv_rv_str])
    
    # Hiển thị bảng summary
    print("\n=== Summary ===")
    headers = ["STT", "Substat", "Tổng giá trị", "Số Rolls", "Debug", "CV/RV (%)"]
    print(tabulate(substat_data, headers=headers, tablefmt="grid"))
    
    # Hiển thị kết quả RV và CV với gạch đầu dòng
    print(f"\n- RV (Roll Value): {total_roll_value * 100:.0f}%")
    if crit_rate > 0 or crit_dmg > 0:
        crit_value = 2 * crit_rate + crit_dmg
        print(f"- CV (Crit Value): {crit_value:.2f}")

if __name__ == "__main__":
    main()
