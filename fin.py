import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

def parse_xbrl_file(xml_file):
    """Parse XBRL file and extract financial data"""
    
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Define namespaces
    namespaces = {
        'xbrli': 'http://www.xbrl.org/2003/instance',
        'in-capmkt': 'http://www.sebi.gov.in/xbrl/2025-01-31/in-capmkt'
    }
    
    # Helper function to get value
    def get_value(tag, context='OneD'):
        elem = root.find(f".//in-capmkt:{tag}[@contextRef='{context}']", namespaces)
        return elem.text if elem is not None else None
    
    def get_numeric_value(tag, context='OneD'):
        val = get_value(tag, context)
        return float(val) if val else 0
    
    # Extract company info
    company_name = get_value('NameOfTheCompany')
    stock_symbol = get_value('Symbol')
    
    # Extract Q2 data (OneD context)
    q2_revenue = get_numeric_value('RevenueFromOperations', 'OneD')
    q2_pbt = get_numeric_value('ProfitBeforeTax', 'OneD')
    q2_pat = get_numeric_value('ProfitLossForPeriod', 'OneD')
    q2_pop = get_numeric_value('ProfitOrLossAttributableToOwnersOfParent', 'OneD')
    
    # Extract H1 data (FourD context)
    h1_revenue = get_numeric_value('RevenueFromOperations', 'FourD')
    h1_pbt = get_numeric_value('ProfitBeforeTax', 'FourD')
    h1_pat = get_numeric_value('ProfitLossForPeriod', 'FourD')
    h1_pop = get_numeric_value('ProfitOrLossAttributableToOwnersOfParent', 'FourD')
    
    # EPS data
    basic_eps_q2 = get_numeric_value('BasicEarningsLossPerShareFromContinuingOperations', 'OneD')
    diluted_eps_q2 = get_numeric_value('DilutedEarningsLossPerShareFromContinuingOperations', 'OneD')
    basic_eps_h1 = get_numeric_value('BasicEarningsLossPerShareFromContinuingOperations', 'FourD')
    diluted_eps_h1 = get_numeric_value('DilutedEarningsLossPerShareFromContinuingOperations', 'FourD')
    
    # Discontinued operations
    disc_ops_q2 = get_numeric_value('ProfitLossFromDiscontinuedOperationsAfterTax', 'OneD')
    disc_ops_h1 = get_numeric_value('ProfitLossFromDiscontinuedOperationsAfterTax', 'FourD')
    
    # Calculate Q1 data (H1 - Q2)
    q1_revenue = h1_revenue - q2_revenue
    q1_pat = h1_pat - q2_pat
    
    # Calculate EBITDA (approximation: PBT + Finance Costs + Depreciation)
    finance_costs_q2 = get_numeric_value('FinanceCosts', 'OneD')
    depreciation_q2 = get_numeric_value('DepreciationDepletionAndAmortisationExpense', 'OneD')
    ebitda_q2 = q2_pbt + finance_costs_q2 + depreciation_q2
    
    finance_costs_h1 = get_numeric_value('FinanceCosts', 'FourD')
    depreciation_h1 = get_numeric_value('DepreciationDepletionAndAmortisationExpense', 'FourD')
    ebitda_h1 = h1_pbt + finance_costs_h1 + depreciation_h1
    
    # Cash Flow data
    cfo_h1 = get_numeric_value('CashFlowsFromUsedInOperatingActivities', 'FourD')
    cfi_h1 = get_numeric_value('CashFlowsFromUsedInInvestingActivities', 'FourD')
    cff_h1 = get_numeric_value('CashFlowsFromUsedInFinancingActivities', 'FourD')
    fcf_h1 = cfo_h1 + cfi_h1  # Free Cash Flow = CFO + CFI
    
    # Comprehensive Income
    comp_income_q2 = get_numeric_value('ComprehensiveIncomeForThePeriod', 'OneD')
    comp_income_h1 = get_numeric_value('ComprehensiveIncomeForThePeriod', 'FourD')
    oci_q2 = get_numeric_value('OtherComprehensiveIncomeNetOfTaxes', 'OneD')
    oci_h1 = get_numeric_value('OtherComprehensiveIncomeNetOfTaxes', 'FourD')
    
    # QoQ Growth (Q2 vs Q1)
    qoq_revenue = ((q2_revenue - q1_revenue) / q1_revenue * 100) if q1_revenue != 0 else 0
    qoq_pat = ((q2_pat - q1_pat) / q1_pat * 100) if q1_pat != 0 else 0
    
    # Calculate margins and additional metrics
    # For Gross Profit - use Income - Expenses (before depreciation)
    total_expenses_q2 = get_numeric_value('Expenses', 'OneD')
    total_expenses_h1 = get_numeric_value('Expenses', 'FourD')
    
    # Gross Profit (approximation: Revenue - Direct Costs)
    cost_materials_q2 = get_numeric_value('CostOfMaterialsConsumed', 'OneD')
    purchases_q2 = get_numeric_value('PurchasesOfStockInTrade', 'OneD')
    inventory_change_q2 = get_numeric_value('ChangesInInventoriesOfFinishedGoodsWorkInProgressAndStockInTrade', 'OneD')
    employee_cost_q2 = get_numeric_value('EmployeeBenefitExpense', 'OneD')
    
    cost_materials_h1 = get_numeric_value('CostOfMaterialsConsumed', 'FourD')
    purchases_h1 = get_numeric_value('PurchasesOfStockInTrade', 'FourD')
    inventory_change_h1 = get_numeric_value('ChangesInInventoriesOfFinishedGoodsWorkInProgressAndStockInTrade', 'FourD')
    employee_cost_h1 = get_numeric_value('EmployeeBenefitExpense', 'FourD')
    
    # Gross Profit = Revenue - (Materials + Purchases + Inventory Change + Employee Costs)
    gross_profit_q2 = q2_revenue - (cost_materials_q2 + purchases_q2 + inventory_change_q2 + employee_cost_q2)
    gross_profit_h1 = h1_revenue - (cost_materials_h1 + purchases_h1 + inventory_change_h1 + employee_cost_h1)
    
    # Operating Profit = EBITDA (or PBT + Finance Costs + Depreciation)
    operating_profit_q2 = ebitda_q2
    operating_profit_h1 = ebitda_h1
    
    # Profit Margins
    gross_margin_q2 = (gross_profit_q2 / q2_revenue * 100) if q2_revenue != 0 else 0
    operating_margin_q2 = (operating_profit_q2 / q2_revenue * 100) if q2_revenue != 0 else 0
    net_margin_q2 = (q2_pat / q2_revenue * 100) if q2_revenue != 0 else 0
    
    gross_margin_h1 = (gross_profit_h1 / h1_revenue * 100) if h1_revenue != 0 else 0
    operating_margin_h1 = (operating_profit_h1 / h1_revenue * 100) if h1_revenue != 0 else 0
    net_margin_h1 = (h1_pat / h1_revenue * 100) if h1_revenue != 0 else 0
    
    # Price Volume Mix (PVM) Analysis
    # Volume = Revenue growth, Price/Mix = Margin expansion/contraction
    revenue_growth_h1 = ((h1_revenue / (h1_revenue - q2_revenue) - 1) * 100) if (h1_revenue - q2_revenue) != 0 else 0
    margin_change = net_margin_q2 - (net_margin_h1 - net_margin_q2) if net_margin_h1 != 0 else 0
    
    # Volume Impact: High volume (>15% growth) vs Low volume (<5% growth)
    volume_category = "High Volume" if abs(qoq_revenue) > 15 else ("Medium Volume" if abs(qoq_revenue) > 5 else "Low Volume")
    
    # Price/Mix Impact: Margin expansion or contraction
    if margin_change > 1:
        pvm_analysis = f"{volume_category} + Price/Mix Positive (Margin ↑)"
    elif margin_change < -1:
        pvm_analysis = f"{volume_category} + Price/Mix Negative (Margin ↓)"
    else:
        pvm_analysis = f"{volume_category} + Price/Mix Stable"
    
    # Convert all values to Crores
    # Data in XML is stored as base units (e.g., 10000000000 = 1000 Crores)
    # So we divide by 10000000 to convert to Crores
    def to_crores(value):
        return round(value / 10000000, 2) if value else 0
    
    # Compile data
    data = {
        'Company Name': company_name,
        'Stock Symbol': stock_symbol,
        
        # Revenue
        'Q2 Revenue (Cr)': to_crores(q2_revenue),
        'H1 Revenue (Cr)': to_crores(h1_revenue),
        
        # Profitability
        'Q2 PBT (Cr)': to_crores(q2_pbt),
        'Q2 PAT (Cr)': to_crores(q2_pat),
        'Q2 POP (Cr)': to_crores(q2_pop),
        'H1 PBT (Cr)': to_crores(h1_pbt),
        'H1 PAT (Cr)': to_crores(h1_pat),
        'H1 POP (Cr)': to_crores(h1_pop),
        
        # EPS (already in per share, no conversion needed)
        'Q2 Basic EPS': round(basic_eps_q2, 2),
        'Q2 Diluted EPS': round(diluted_eps_q2, 2),
        'H1 Basic EPS': round(basic_eps_h1, 2),
        'H1 Diluted EPS': round(diluted_eps_h1, 2),
        
        # Discontinued Operations
        'Q2 Discontinued Ops (Cr)': to_crores(disc_ops_q2),
        'H1 Discontinued Ops (Cr)': to_crores(disc_ops_h1),
        
        # Growth Metrics
        'QoQ Revenue Growth (%)': round(qoq_revenue, 2),
        'QoQ PAT Growth (%)': round(qoq_pat, 2),
        
        # EBITDA
        'Q2 EBITDA (Cr)': to_crores(ebitda_q2),
        'H1 EBITDA (Cr)': to_crores(ebitda_h1),
        'Q2 EBITDA Margin (%)': round((ebitda_q2 / q2_revenue * 100), 2) if q2_revenue != 0 else 0,
        
        # Profitability Margins
        'Q2 Gross Profit (Cr)': to_crores(gross_profit_q2),
        'Q2 Gross Profit Margin (%)': round(gross_margin_q2, 2),
        'Q2 Operating Profit (Cr)': to_crores(operating_profit_q2),
        'Q2 Operating Profit Margin (%)': round(operating_margin_q2, 2),
        'Q2 Net Profit Margin (%)': round(net_margin_q2, 2),
        
        'H1 Gross Profit (Cr)': to_crores(gross_profit_h1),
        'H1 Gross Profit Margin (%)': round(gross_margin_h1, 2),
        'H1 Operating Profit (Cr)': to_crores(operating_profit_h1),
        'H1 Operating Profit Margin (%)': round(operating_margin_h1, 2),
        'H1 Net Profit Margin (%)': round(net_margin_h1, 2),
        
        # Volume & PVM Analysis
        'Volume Category': volume_category,
        'PVM Analysis': pvm_analysis,
        'Margin Change (bps)': round(margin_change * 100, 0),  # in basis points
        
        # Cash Flow
        'H1 CFO (Cr)': to_crores(cfo_h1),
        'H1 CFI (Cr)': to_crores(cfi_h1),
        'H1 CFF (Cr)': to_crores(cff_h1),
        'H1 FCF (Cr)': to_crores(fcf_h1),
        
        # Comprehensive Income
        'Q2 Comprehensive Income (Cr)': to_crores(comp_income_q2),
        'Q2 OCI (Cr)': to_crores(oci_q2),
        'H1 Comprehensive Income (Cr)': to_crores(comp_income_h1),
        'H1 OCI (Cr)': to_crores(oci_h1),
    }
    
    return data

def merge_financial_data(file_list):
    """Merge financial data from multiple XBRL files"""
    
    all_data = []
    
    for xml_file in file_list:
        try:
            data = parse_xbrl_file(xml_file)
            all_data.append(data)
            print(f"Successfully processed: {xml_file}")
        except Exception as e:
            print(f"Error processing {xml_file}: {str(e)}")
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    return df

# Main execution
if __name__ == "__main__":
    # List your XBRL files
    xml_files = ['1.xml', '2.xml']  # TCS and Edelweiss files
    
    # Process and merge data
    merged_df = merge_financial_data(xml_files)
    
    # Display results
    print("\n" + "="*120)
    print("║" + " "*118 + "║")
    print("║" + " "*35 + "📊 COMPREHENSIVE FINANCIAL ANALYSIS REPORT 📊" + " "*38 + "║")
    print("║" + " "*45 + "Q2 & H1 FY 2025-26" + " "*52 + "║")
    print("║" + " "*118 + "║")
    print("="*120)
    print(merged_df.to_string(index=False))
    
    # Export to Excel
    output_file = f'financial_analysis_{datetime.now().strftime("%Y%m%d")}.xlsx'
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        merged_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Create separate sheets for detailed metrics
        revenue_cols = ['Company Name', 'Stock Symbol', 'Q2 Revenue (Cr)', 'H1 Revenue (Cr)', 
                       'QoQ Revenue Growth (%)', 'Volume Category']
        merged_df[revenue_cols].to_excel(writer, sheet_name='Revenue Analysis', index=False)
        
        profitability_cols = ['Company Name', 'Stock Symbol', 'Q2 PBT (Cr)', 'Q2 PAT (Cr)', 
                             'Q2 POP (Cr)', 'H1 PBT (Cr)', 'H1 PAT (Cr)', 'H1 POP (Cr)']
        merged_df[profitability_cols].to_excel(writer, sheet_name='Profitability', index=False)
        
        margin_cols = ['Company Name', 'Stock Symbol', 'Q2 Gross Profit Margin (%)', 
                      'Q2 Operating Profit Margin (%)', 'Q2 Net Profit Margin (%)',
                      'H1 Gross Profit Margin (%)', 'H1 Operating Profit Margin (%)', 
                      'H1 Net Profit Margin (%)', 'Margin Change (bps)']
        merged_df[margin_cols].to_excel(writer, sheet_name='Margin Analysis', index=False)
        
        pvm_cols = ['Company Name', 'Stock Symbol', 'QoQ Revenue Growth (%)', 
                   'Volume Category', 'PVM Analysis', 'Margin Change (bps)',
                   'Q2 Net Profit Margin (%)', 'H1 Net Profit Margin (%)']
        merged_df[pvm_cols].to_excel(writer, sheet_name='PVM Analysis', index=False)
        
        eps_cols = ['Company Name', 'Stock Symbol', 'Q2 Basic EPS', 'Q2 Diluted EPS', 
                   'H1 Basic EPS', 'H1 Diluted EPS']
        merged_df[eps_cols].to_excel(writer, sheet_name='EPS Analysis', index=False)
        
        cashflow_cols = ['Company Name', 'Stock Symbol', 'H1 CFO (Cr)', 'H1 CFI (Cr)', 
                        'H1 CFF (Cr)', 'H1 FCF (Cr)']
        merged_df[cashflow_cols].to_excel(writer, sheet_name='Cash Flow', index=False)
    
    print(f"\n✅ Data exported to {output_file}")
    
    print("\n" + "="*120)
    print("║" + " "*118 + "║")
    print("║" + " "*40 + "📋 EXECUTIVE SUMMARY - KEY METRICS 📋" + " "*40 + "║")
    print("║" + " "*118 + "║")
    print("="*120)
    
    for idx, row in merged_df.iterrows():
        print(f"\n{'┌' + '─'*118 + '┐'}")
        print(f"│ 🏢 {row['Company Name']:^114s} │")
        print(f"│    Stock Symbol: {row['Stock Symbol']:<102s} │")
        print(f"{'├' + '─'*118 + '┤'}")
        
        print(f"│                                                                                                                      │")
        print(f"│  📊 REVENUE & GROWTH METRICS                                                                                         │")
        print(f"│  {'─'*116}  │")
        print(f"│    • Q2 FY26 Revenue:          ₹{row['Q2 Revenue (Cr)']:>12,.2f} Cr    │    H1 FY26 Revenue:          ₹{row['H1 Revenue (Cr)']:>12,.2f} Cr    │")
        print(f"│    • QoQ Revenue Growth:       {row['QoQ Revenue Growth (%)']:>12.2f} %     │    Volume Category:          {row['Volume Category']:<20s}    │")
        print(f"│                                                                                                                      │")
        
        print(f"│  💰 PROFITABILITY ANALYSIS                                                                                           │")
        print(f"│  {'─'*116}  │")
        print(f"│    • Q2 PBT:                   ₹{row['Q2 PBT (Cr)']:>12,.2f} Cr    │    Q2 PAT:                   ₹{row['Q2 PAT (Cr)']:>12,.2f} Cr    │")
        print(f"│    • Q2 POP:                   ₹{row['Q2 POP (Cr)']:>12,.2f} Cr    │    PAT Growth (QoQ):         {row['QoQ PAT Growth (%)']:>12.2f} %     │")
        print(f"│    • Basic EPS (Q2):           ₹{row['Q2 Basic EPS']:>12.2f}        │    Diluted EPS (Q2):         ₹{row['Q2 Diluted EPS']:>12.2f}        │")
        print(f"│                                                                                                                      │")
        
        print(f"│  📈 MARGIN ANALYSIS (Profitability Ratios)                                                                           │")
        print(f"│  {'─'*116}  │")
        print(f"│    • Gross Profit Margin:      {row['Q2 Gross Profit Margin (%)']:>12.2f} %     │    Operating Profit Margin:  {row['Q2 Operating Profit Margin (%)']:>12.2f} %     │")
        print(f"│    • Net Profit Margin:        {row['Q2 Net Profit Margin (%)']:>12.2f} %     │    EBITDA Margin:            {row['Q2 EBITDA Margin (%)']:>12.2f} %     │")
        print(f"│    • Q2 EBITDA:                ₹{row['Q2 EBITDA (Cr)']:>12,.2f} Cr    │    Margin Change:            {row['Margin Change (bps)']:>12.0f} bps    │")
        print(f"│                                                                                                                      │")
        
        print(f"│  🔄 PRICE-VOLUME-MIX (PVM) INSIGHTS                                                                                  │")
        print(f"│  {'─'*116}  │")
        print(f"│    • Analysis: {row['PVM Analysis']:<102s} │")
        print(f"│    • Interpretation: {'Strong pricing power with volume growth' if 'Positive' in row['PVM Analysis'] else 'Margin pressure despite volume' if 'Negative' in row['PVM Analysis'] else 'Stable operational efficiency':<84s} │")
        print(f"│                                                                                                                      │")
        
        print(f"│  💵 CASH FLOW STATEMENT (H1 FY26)                                                                                    │")
        print(f"│  {'─'*116}  │")
        print(f"│    • Operating Cash Flow:      ₹{row['H1 CFO (Cr)']:>12,.2f} Cr    │    Investing Cash Flow:      ₹{row['H1 CFI (Cr)']:>12,.2f} Cr    │")
        print(f"│    • Financing Cash Flow:      ₹{row['H1 CFF (Cr)']:>12,.2f} Cr    │    Free Cash Flow:           ₹{row['H1 FCF (Cr)']:>12,.2f} Cr    │")
        print(f"│                                                                                                                      │")
        
        print(f"│  🎯 COMPREHENSIVE INCOME                                                                                             │")
        print(f"│  {'─'*116}  │")
        print(f"│    • Q2 Total Comprehensive:   ₹{row['Q2 Comprehensive Income (Cr)']:>12,.2f} Cr    │    Q2 OCI:                   ₹{row['Q2 OCI (Cr)']:>12,.2f} Cr    │")
        print(f"│    • H1 Total Comprehensive:   ₹{row['H1 Comprehensive Income (Cr)']:>12,.2f} Cr    │    H1 OCI:                   ₹{row['H1 OCI (Cr)']:>12,.2f} Cr    │")
        print(f"│                                                                                                                      │")
        print(f"{'└' + '─'*118 + '┘'}")
    
    print("\n" + "="*120)
    print(f"Report Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}")
    print("="*120)