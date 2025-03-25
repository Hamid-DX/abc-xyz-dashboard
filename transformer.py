# Helper functions
def calculate_mode(series):
    return series.mode().iloc[0] if not series.mode().empty else None

def condition_abc_margin(x):
    if x <= 0.03:
        return 'C'
    elif x > 0.03 and x <= 0.07:
        return 'B'
    else:
        return 'A'

def condition_abc_rev(x):
    if x > 0 and x <= 0.80:
        return "A"
    elif x > 0.80 and x <= 0.95:
        return "B"
    else:
        return 'C'

def condition_xyz(x):
    if x <= 0.5:
        return 'X'
    elif x > 0.5 and x <= 1:
        return 'Y'
    else:
        return 'Z'

# ABC Analysis
def abc_analysis(df):
    """
    Perform ABC analysis on the filtered dataset
    
    Parameters:
    df (pandas.DataFrame): Filtered raw data
    
    Returns:
    pandas.DataFrame: ABC analysis results
    """
    abc = df[['TERRITORY', 'DELIVERY_NO', 'CATALOG', 'INVENTORY', 'REVENUE_VAT_EXCL', 
              'AD_FR_MARGIN', 'AD_FR_MARGIN%']]
    
    # ABC Margin Analysis
    abc_df_mode_with_ter = abc.groupby(['TERRITORY', 'INVENTORY']).agg(
        PRODUCT_MARGIN=('AD_FR_MARGIN%', calculate_mode),  
        Revenue=('REVENUE_VAT_EXCL', 'sum')
    ).reset_index()
    abc_df_mode_with_ter['ABC_MARGIN_MODE'] = abc_df_mode_with_ter['PRODUCT_MARGIN'].apply(condition_abc_margin)

    # ABC Revenue Analysis
    abc_rev_with_ter = abc.groupby(['TERRITORY', 'INVENTORY']).agg(
        TOTAL_REVENUE=('REVENUE_VAT_EXCL', 'sum')).reset_index()
    
    abc_rev_with_ter['TOTAL_REVENUE_sum'] = abc_rev_with_ter.groupby('TERRITORY')['TOTAL_REVENUE'].transform('sum')
    abc_rev_with_ter = abc_rev_with_ter.sort_values(by=['TERRITORY', 'TOTAL_REVENUE'], ascending=[True, False])
    abc_rev_with_ter['CUMULATIVE_SUM'] = abc_rev_with_ter.groupby('TERRITORY')['TOTAL_REVENUE'].cumsum()
    abc_rev_with_ter['SKU_REV%'] = abc_rev_with_ter['CUMULATIVE_SUM'] / abc_rev_with_ter['TOTAL_REVENUE_sum']
    abc_rev_with_ter['ABC_REVENUE'] = abc_rev_with_ter['SKU_REV%'].apply(condition_abc_rev)

    # Merge ABC Revenue and Margin datasets
    final_ter = abc_rev_with_ter.merge(abc_df_mode_with_ter, on=['TERRITORY', 'INVENTORY'], how='left')
    final_ter['ABC(REV-MAR)'] = final_ter['ABC_REVENUE'].astype(str) + final_ter['ABC_MARGIN_MODE'].astype(str)

    return final_ter[['TERRITORY', 'INVENTORY', 'TOTAL_REVENUE', 'ABC_REVENUE', 'PRODUCT_MARGIN', 
                      'ABC_MARGIN_MODE', 'ABC(REV-MAR)']]

# XYZ Analysis
def xyz_analysis(df):
    """
    Perform XYZ analysis on the filtered dataset
    
    Parameters:
    df (pandas.DataFrame): Filtered raw data
    
    Returns:
    pandas.DataFrame: XYZ analysis results
    """
    xyz = df[['TERRITORY', 'DN_DELIVERY_DT', 'INVENTORY', 'REVENUE_VAT_EXCL']]
    xyz['YEAR'] = xyz['DN_DELIVERY_DT'].dt.year
    xyz['MONTH'] = xyz['DN_DELIVERY_DT'].dt.month
    xyz['YEAR_MONTH'] = xyz['MONTH'].astype(str) + '-' + xyz['YEAR'].astype(str)

    xyz_df_ter = xyz.groupby(['TERRITORY', 'INVENTORY', 'YEAR_MONTH'])['REVENUE_VAT_EXCL'].sum().reset_index()
    xyz_df_ter = xyz_df_ter.pivot(index=['TERRITORY', 'INVENTORY'], columns='YEAR_MONTH', 
                                   values='REVENUE_VAT_EXCL').reset_index().fillna(0)

    # Identify sales columns dynamically
    sales_columns = [col for col in xyz_df_ter.columns if col not in ['TERRITORY', 'INVENTORY']]

    # Calculate total revenue, average revenue, and standard deviation dynamically
    xyz_df_ter['TOTAL_REVENUE'] = xyz_df_ter[sales_columns].sum(axis=1, numeric_only=True)
    num_months = len(sales_columns)
    xyz_df_ter['AVERAGE_REVENUE'] = xyz_df_ter['TOTAL_REVENUE'] / num_months if num_months > 0 else 0
    xyz_df_ter['STD_DEV'] = xyz_df_ter[sales_columns].std(axis=1, numeric_only=True)

    # Calculate Coefficient of Variance (CoV)
    xyz_df_ter['CoV'] = xyz_df_ter['STD_DEV'] / xyz_df_ter['AVERAGE_REVENUE']
    # Replace infinity with a high number and NaN with 0
    xyz_df_ter['CoV'] = xyz_df_ter['CoV'].replace([float('inf'), float('-inf')], 999).fillna(0)
    xyz_df_ter['TERRITORY_XYZ'] = xyz_df_ter['CoV'].apply(condition_xyz)

    return xyz_df_ter[['TERRITORY', 'INVENTORY', 'TOTAL_REVENUE', 'CoV', 'STD_DEV', 'AVERAGE_REVENUE', 'TERRITORY_XYZ']]

# ABC-XYZ Merging
def merge_abc_xyz(territory_abc_df, xyz_df):
    """
    Merge ABC and XYZ analysis results
    
    Parameters:
    territory_abc_df (pandas.DataFrame): ABC analysis results
    xyz_df (pandas.DataFrame): XYZ analysis results
    
    Returns:
    pandas.DataFrame: Combined ABC-XYZ analysis
    """
    abc_xyz = territory_abc_df.merge(xyz_df, on=['TERRITORY', 'INVENTORY'], how='left')
    # Use TOTAL_REVENUE_x as the main TOTAL_REVENUE to avoid confusion
    abc_xyz['TOTAL_REVENUE'] = abc_xyz['TOTAL_REVENUE_x']
    abc_xyz['ABC_XYZ'] = abc_xyz['ABC(REV-MAR)'].astype(str) + abc_xyz['TERRITORY_XYZ'].astype(str)
    
    # Select only the necessary columns
    result_columns = [
        'TERRITORY', 'INVENTORY', 'TOTAL_REVENUE', 'ABC_REVENUE',
        'PRODUCT_MARGIN', 'ABC_MARGIN_MODE', 'ABC(REV-MAR)',
        'CoV', 'STD_DEV', 'AVERAGE_REVENUE', 'TERRITORY_XYZ', 'ABC_XYZ'
    ]
    
    return abc_xyz[result_columns]