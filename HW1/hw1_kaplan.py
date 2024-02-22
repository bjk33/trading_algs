import pandas as pd

# Load Unmatched Blotter
unmatched_blotter = pd.read_csv('~/Desktop/FINTECH533/HW1/hw1-1.csv')


# Sort the original DataFrame by identifier and timestamp
unmatched_blotter = unmatched_blotter.sort_values(by=['identifier', 'timestamp'])
# Store original indexing for consistency across data frames
unmatched_blotter['original_index'] = unmatched_blotter.index


def match_trades(unmatched_blotter_df):
    # Initialize the output DataFrames

    matched_columns = [
        'entry_date', 'identifier', 'entry_time', 'entry_qty', 'entry_price', 'exit_date', 'exit_time', 'exit_price'
    ]

    matched_blotter = pd.DataFrame(columns=matched_columns)
    unmatched_entries = pd.DataFrame(columns=unmatched_blotter.columns)
    unmatched_exits = pd.DataFrame(columns=unmatched_blotter.columns)

    # Temporary storage for pending ENTRY trades
    temporary_storage = {}

    for index, row in unmatched_blotter_df.iterrows():
        # Extract necessary information from the row
        identifier = row['identifier']
        trade_date = row['date']
        trade_time = row['timestamp']
        trade_qty = row['qty']
        trade_price = row['price']
        trade_trip = row['trip']

        # Check for same timestamp entries and exits
        if identifier in temporary_storage and temporary_storage[identifier]['timestamp'] == trade_time:
            # Treat both trades as unmatched
            unmatched_entries = unmatched_entries.append(temporary_storage[identifier], ignore_index=True)
            unmatched_exits = unmatched_exits.append(row, ignore_index=True)
            del temporary_storage[identifier]
            continue

        # Process entries and exits
        if trade_trip == 'ENTRY':
            # Add entry to temporary storage
            temporary_storage[identifier] = row
        elif trade_trip == 'EXIT':
            if identifier in temporary_storage:
                entry_trade = temporary_storage[identifier]
                entry_qty = entry_trade['qty']

                # Check if ENTRY and EXIT quantities have the same sign
                if (entry_qty * trade_qty) > 0:
                    # Treat as unmatched if both quantities have the same sign
                    unmatched_exits = unmatched_exits.append(row, ignore_index=True)
                elif abs(trade_qty) <= abs(entry_qty):
                    # Partial or full match
                    matched_trade = {
                        'entry_date': entry_trade['date'],
                        'identifier': identifier,
                        'entry_time': entry_trade['timestamp'],
                        'entry_qty': min(abs(trade_qty), abs(entry_qty)),
                        'entry_price': entry_trade['price'],
                        'exit_date': trade_date,
                        'exit_time': trade_time,
                        'exit_qty': abs(trade_qty),
                        'exit_price': trade_price
                    }
                    matched_blotter = matched_blotter.append(matched_trade, ignore_index=True)

                    # Update entry quantity in temporary storage or remove if fully matched
                    if abs(trade_qty) < abs(entry_qty):
                        temporary_storage[identifier]['qty'] -= trade_qty
                    else:
                        del temporary_storage[identifier]

                else:
                    # Exit quantity exceeds entry quantity
                    matched_trade = {
                        'entry_date': entry_trade['date'],
                        'identifier': identifier,
                        'entry_time': entry_trade['timestamp'],
                        'entry_qty': abs(entry_qty),
                        'entry_price': entry_trade['price'],
                        'exit_date': trade_date,
                        'exit_time': trade_time,
                        'exit_qty': abs(entry_qty),
                        'exit_price': trade_price
                    }
                    matched_blotter = matched_blotter.append(matched_trade, ignore_index=True)
                    unmatched_exits = unmatched_exits.append({
                        'identifier': identifier,
                        'date': trade_date,
                        'timestamp': trade_time,
                        'qty': trade_qty + entry_qty,
                        'price': trade_price,
                        'trip': 'EXIT'
                    }, ignore_index=True)
                    del temporary_storage[identifier]

            else:
                # No matching entry found
                unmatched_exits = unmatched_exits.append(row, ignore_index=True)

    # Append remaining unmatched entries after iteration
    for entry in temporary_storage.values():
        unmatched_entries = unmatched_entries.append(entry, ignore_index=True)

    return matched_blotter, unmatched_entries, unmatched_exits
