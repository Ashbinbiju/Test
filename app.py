# app.py

import decimal
from flask import Flask, render_template, request

# --- Setup ---
app = Flask(__name__)
# Use the Decimal module for precise financial calculations
decimal.getcontext().prec = 10

# --- Helper Functions (copied from CLI version) ---
def rnd(value):
    return decimal.Decimal(value).quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_UP)

def get_third_decimal(value):
    s_value = str(decimal.Decimal(value).quantize(decimal.Decimal('0.001')))
    if '.' in s_value and len(s_value.split('.')[1]) >= 3:
        return int(s_value[-1])
    return 0
    
def calculate_tax_components(taxable_base, tax1_rate, tax2_rate):
    total_tax_rate = tax1_rate + tax2_rate
    total_tax_direct = rnd(taxable_base * (total_tax_rate / 100))
    tax1_raw = taxable_base * (tax1_rate / 100)
    tax2_raw = taxable_base * (tax2_rate / 100)
    tax1 = rnd(tax1_raw)
    tax2 = rnd(tax2_raw)
    
    if tax1 + tax2 != total_tax_direct:
        diff = total_tax_direct - (tax1 + tax2)
        t1_third_dec = get_third_decimal(tax1_raw)
        t2_third_dec = get_third_decimal(tax2_raw)

        if t1_third_dec > t2_third_dec:
            tax1 += diff
        elif t2_third_dec > t1_third_dec:
            tax2 += diff
        else:
            if tax1_rate >= tax2_rate:
                tax1 += diff
            else:
                tax2 += diff
    return tax1, tax2, total_tax_direct

# --- Main Calculation Logic ---
def perform_calculation(scenario, data):
    summary = {}
    price = data['price']
    d1_rate = data['d1_rate']
    d2_rate = data['d2_rate']
    tax1_rate = data['tax1_rate']
    tax2_rate = data['tax2_rate']
    edge_rate = data['edge_rate']
    bag_price = data['bag_price']
    bag_qty = data['bag_qty']

    total_tax_rate = tax1_rate + tax2_rate
    has_discount = scenario in ['1', '2', '5', '6']
    has_edge_fee = scenario in ['1', '2', '3', '4']
    
    total = decimal.Decimal('0')

    if scenario == '1': # Tax-Inclusive + Discount + Edge Fee
        summary['Scenario'] = "Tax-Inclusive Item + Discount + Edge Fee"
        d1 = rnd(price * (d1_rate / 100))
        d2 = rnd((price - d1) * (d2_rate / 100))
        total_discount = d1 + d2
        price_after_discount = price - total_discount
        edge_fee = rnd(price_after_discount * (edge_rate / 100))
        price_with_edge_fee = price + edge_fee
        tax_exclusive_base = rnd((price_with_edge_fee * 100) / (100 + total_tax_rate))
        tax1, tax2, total_tax = calculate_tax_components(tax_exclusive_base, tax1_rate, tax2_rate)
        total = tax_exclusive_base - total_discount + total_tax
        summary.update({'Tax-Inc Price': price, 'Discount 1': d1, 'Discount 2': d2, 'Total Discount': total_discount, 'Base for Edge Fee': price_after_discount, 'Edge Fee': edge_fee, 'Tax-Exc Base (Edge SP)': tax_exclusive_base, 'Tax 1': tax1, 'Tax 2': tax2, 'Total Tax': total_tax, 'Sub-Total (Item)': total})

    elif scenario == '2': # Tax-Exclusive + Discount + Edge Fee
        summary['Scenario'] = "Tax-Exclusive Item + Discount + Edge Fee"
        d1 = rnd(price * (d1_rate / 100))
        d2 = rnd((price - d1) * (d2_rate / 100))
        total_discount = d1 + d2
        price_after_discount = price - total_discount
        edge_fee = rnd(price_after_discount * (edge_rate / 100))
        edge_sp = price + edge_fee
        taxable_base = edge_sp - total_discount
        tax1, tax2, total_tax = calculate_tax_components(taxable_base, tax1_rate, tax2_rate)
        total = edge_sp - total_discount + total_tax
        summary.update({'Selling Price': price, 'Discount 1': d1, 'Discount 2': d2, 'Total Discount': total_discount, 'Edge Fee': edge_fee, 'Edge Selling Price': edge_sp, 'Taxable Base': taxable_base, 'Tax 1': tax1, 'Tax 2': tax2, 'Total Tax': total_tax, 'Sub-Total (Item)': total})
    
    # Add other scenarios here...
    elif scenario == '3': # Tax-Inclusive + Edge Fee (No Discount)
        summary['Scenario'] = "Tax-Inclusive Item + Edge Fee (No Discount)"
        edge_fee = rnd(price * (edge_rate / 100))
        price_with_edge_fee = price + edge_fee
        tax_exclusive_base = rnd((price_with_edge_fee * 100) / (100 + total_tax_rate))
        tax1, tax2, total_tax = calculate_tax_components(tax_exclusive_base, tax1_rate, tax2_rate)
        total = tax_exclusive_base + total_tax
        summary.update({'Tax-Inc Price': price, 'Edge Fee': edge_fee, 'Tax-Exc Base (Edge SP)': tax_exclusive_base, 'Tax 1': tax1, 'Tax 2': tax2, 'Total Tax': total_tax, 'Sub-Total (Item)': total})

    elif scenario == '4': # Tax-Exclusive + Edge Fee (No Discount)
        summary['Scenario'] = "Tax-Exclusive Item + Edge Fee (No Discount)"
        edge_fee = rnd(price * (edge_rate / 100))
        edge_sp = price + edge_fee
        taxable_base = price
        tax1, tax2, total_tax = calculate_tax_components(taxable_base, tax1_rate, tax2_rate)
        total = edge_sp + total_tax
        summary.update({'Selling Price': price, 'Edge Fee': edge_fee, 'Edge Selling Price': edge_sp, 'Taxable Base': taxable_base, 'Tax 1': tax1, 'Tax 2': tax2, 'Total Tax': total_tax, 'Sub-Total (Item)': total})

    elif scenario == '5': # Normal Tax-Exclusive (with discount)
        summary['Scenario'] = "Normal Tax-Exclusive (with discount)"
        d1 = rnd(price * (d1_rate / 100))
        d2 = rnd((price - d1) * (d2_rate / 100))
        total_discount = d1 + d2
        taxable_base = price - total_discount
        tax1, tax2, total_tax = calculate_tax_components(taxable_base, tax1_rate, tax2_rate)
        total = taxable_base + total_tax
        summary.update({'Selling Price': price, 'Discount 1': d1, 'Discount 2': d2, 'Total Discount': total_discount, 'Taxable Base': taxable_base, 'Tax 1': tax1, 'Tax 2': tax2, 'Total Tax': total_tax, 'Sub-Total (Item)': total})
    
    elif scenario == '6': # Normal Tax-Inclusive (with discount)
        summary['Scenario'] = "Normal Tax-Inclusive (with discount)"
        tax_exclusive_base = rnd((price * 100) / (100 + total_tax_rate))
        d1 = rnd(price * (d1_rate / 100))
        d2 = rnd((price - d1) * (d2_rate / 100))
        total_discount = d1 + d2
        tax1, tax2, total_tax = calculate_tax_components(tax_exclusive_base, tax1_rate, tax2_rate)
        total = tax_exclusive_base - total_discount + total_tax
        summary.update({'Tax-Inc Price': price, 'Tax-Exc Price (Receipt)': tax_exclusive_base, 'Discount 1': d1, 'Discount 2': d2, 'Total Discount': total_discount, 'Tax 1': tax1, 'Tax 2': tax2, 'Total Tax': total_tax, 'Sub-Total (Item)': total})
    
    # Bag Fee Calculation
    final_total = total
    if bag_qty > 0 and bag_price > 0:
        if has_edge_fee and edge_rate > 0:
            edge_fee_for_bag = rnd(bag_price * (edge_rate / 100))
            total_bag_fee = (bag_price + edge_fee_for_bag) * bag_qty
            summary['Edge Bag Fee'] = total_bag_fee
        else:
            total_bag_fee = bag_price * bag_qty
            summary['Bag Fee'] = total_bag_fee
        final_total += total_bag_fee

    summary['FINAL TOTAL'] = final_total
    return summary

# --- Flask Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    if request.method == 'POST':
        # Get data from form and convert to Decimal
        scenario = request.form.get('scenario')
        form_data = {
            'price': decimal.Decimal(request.form.get('price', '0')),
            'd1_rate': decimal.Decimal(request.form.get('d1_rate', '0')),
            'd2_rate': decimal.Decimal(request.form.get('d2_rate', '0')),
            'tax1_rate': decimal.Decimal(request.form.get('tax1_rate', '0')),
            'tax2_rate': decimal.Decimal(request.form.get('tax2_rate', '0')),
            'edge_rate': decimal.Decimal(request.form.get('edge_rate', '0')),
            'bag_price': decimal.Decimal(request.form.get('bag_price', '0')),
            'bag_qty': decimal.Decimal(request.form.get('bag_qty', '0')),
        }
        results = perform_calculation(scenario, form_data)

    return render_template('calculator.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
