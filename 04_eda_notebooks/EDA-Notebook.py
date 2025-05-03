import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_excel(r"D:\Projects\Not_completed\Educational_Employment_Data_Project\nirf_pdfs\NIRF_Placements_Split_Yearwise.xlsx")
df.columns = df.columns.str.strip()

ug_df = df[df['Program'].str.contains("UG", case=False)]

fig, axs = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('UG Engineering Program Insights (Placements + Salary)', fontsize=18)

# 1. Average Median Salary by Program
avg_salary = ug_df.groupby('Program')['Median Salary (LPA)'].mean().sort_values()
sns.barplot(x=avg_salary.index, y=avg_salary.values, palette='Blues_d', ax=axs[0, 0])
axs[0, 0].set_title('Avg Median Salary by UG Program')
axs[0, 0].set_ylabel('Median Salary (LPA)')
axs[0, 0].tick_params(axis='x', rotation=45)

# 2. Salary Trend Over Years
sns.lineplot(data=ug_df, x='Year', y='Median Salary (LPA)', hue='Program', marker='o', ax=axs[0, 1])
axs[0, 1].set_title('Salary Trend by Year (UG)')
axs[0, 1].grid(True)

# 3. Placement % by Program
sns.boxplot(x='Program', y='Placement %', data=ug_df, palette='coolwarm', ax=axs[1, 0])
axs[1, 0].set_title('Placement % by UG Program')
axs[1, 0].tick_params(axis='x', rotation=45)

# 4. Top Colleges by Median Salary
top_colleges = ug_df.groupby('College Name')['Median Salary (LPA)'].mean().sort_values(ascending=False).head(10)
sns.barplot(x=top_colleges.values, y=top_colleges.index, palette='viridis', ax=axs[1, 1])
axs[1, 1].set_title('Top UG Colleges by Median Salary')
axs[1, 1].set_xlabel('Median Salary (LPA)')

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()
