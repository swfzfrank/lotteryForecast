import lottery

if __name__ == "__main__":
    if lottery.get_history_ssq_data().empty:
        lottery.fetch_ssq_all_data()
    else:
        lottery.update_ssq_data()