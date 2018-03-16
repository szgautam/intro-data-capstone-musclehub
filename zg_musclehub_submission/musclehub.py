
# coding: utf-8

# # Capstone Project 1: MuscleHub AB Test

# ## Step 1: Get started with SQL

# Like most businesses, Janet keeps her data in a SQL database.  Normally, you'd download the data from her database to a csv file, and then load it into a Jupyter Notebook using Pandas.
# 
# For this project, you'll have to access SQL in a slightly different way.  You'll be using a special Codecademy library that lets you type SQL queries directly into this Jupyter notebook.  You'll have pass each SQL query as an argument to a function called `sql_query`.  Each query will return a Pandas DataFrame.  Here's an example:

# In[1]:


# This import only needs to happen once, at the beginning of the notebook
from codecademySQL import sql_query


# In[2]:


# Here's an example where we save the data to a DataFrame
df = sql_query('''
SELECT *
FROM applications
LIMIT 5
''')


# In[3]:


# Here's an example of a query that just displays some data
sql_query('''
SELECT *
FROM visits
LIMIT 5
''')


# ## Step 2: Get your dataset

# Let's get started!
# 
# Janet of MuscleHub has a SQLite database, which contains several tables that will be helpful to you in this investigation:
# - `visits` contains information about potential gym customers who have visited MuscleHub
# - `fitness_tests` contains information about potential customers in "Group A", who were given a fitness test
# - `applications` contains information about any potential customers (both "Group A" and "Group B") who filled out an application.  Not everyone in `visits` will have filled out an application.
# - `purchases` contains information about customers who purchased a membership to MuscleHub.
# 
# Use the space below to examine each table.

# In[4]:


# Examine visits here
sql_query('''
SELECT *
FROM visits
LIMIT 5
''')


# In[5]:


# Examine fitness_tests here
sql_query('''
SELECT * 
FROM fitness_tests
LIMIT 5
''')


# In[6]:


# Examine applications here
sql_query('''
SELECT *
FROM applications
LIMIT 5
''')


# In[7]:


# Examine purchases here
sql_query('''
SELECT *
FROM purchases
LIMIT 5''')


# We'd like to download a giant DataFrame containing all of this data.  You'll need to write a query that does the following things:
# 
# 1. Not all visits in  `visits` occurred during the A/B test.  You'll only want to pull data where `visit_date` is on or after `7-1-17`.
# 
# 2. You'll want to perform a series of `LEFT JOIN` commands to combine the four tables that we care about.  You'll need to perform the joins on `first_name`, `last_name`, and `email`.  Pull the following columns:
# 
# 
# - `visits.first_name`
# - `visits.last_name`
# - `visits.gender`
# - `visits.email`
# - `visits.visit_date`
# - `fitness_tests.fitness_test_date`
# - `applications.application_date`
# - `purchases.purchase_date`
# 
# Save the result of this query to a variable called `df`.
# 
# Hint: your result should have 5004 rows.  Does it?

# In[8]:


df = sql_query('''
SELECT visits.first_name, visits.last_name, visits.gender, visits.email, visits.visit_date,
    fitness_tests.fitness_test_date, applications.application_date, purchases.purchase_date
FROM visits
LEFT JOIN fitness_tests
    ON fitness_tests.email = visits.email
    AND fitness_tests.first_name = visits.first_name
    AND fitness_tests.last_name = visits.last_name
LEFT JOIN applications
    ON applications.email = visits.email
    AND applications.first_name = visits.first_name
    AND applications.last_name = visits.last_name
LEFT JOIN purchases
    ON purchases.email = visits.email
    AND purchases.first_name = visits.first_name
    AND purchases.last_name = purchases.last_name
WHERE visits.visit_date >= '7-1-17'
''')

print len(df)


# ## Step 3: Investigate the A and B groups

# We have some data to work with! Import the following modules so that we can start doing analysis:
# - `import pandas as pd`
# - `from matplotlib import pyplot as plt`

# In[9]:


import pandas as pd
from matplotlib import pyplot as plt


# We're going to add some columns to `df` to help us with our analysis.
# 
# Start by adding a column called `ab_test_group`.  It should be `A` if `fitness_test_date` is not `None`, and `B` if `fitness_test_date` is `None`.

# In[10]:


df['ab_test_group'] = df.apply(lambda row: 'B' if pd.isnull(row.fitness_test_date) else 'A', axis = 1)


# Let's do a quick sanity check that Janet split her visitors such that about half are in A and half are in B.
# 
# Start by using `groupby` to count how many users are in each `ab_test_group`.  Save the results to `ab_counts`.

# In[11]:


ab_counts = df.groupby(['ab_test_group']).email.count().reset_index()

print ab_counts


# We'll want to include this information in our presentation.  Let's create a pie cart using `plt.pie`.  Make sure to include:
# - Use `plt.axis('equal')` so that your pie chart looks nice
# - Add a legend labeling `A` and `B`
# - Use `autopct` to label the percentage of each group
# - Save your figure as `ab_test_pie_chart.png`

# In[12]:


plt.pie(ab_counts.email, autopct='%.2f%%', colors = ['gainsboro', 'salmon'])
plt.legend(ab_counts.ab_test_group)
plt.axis('equal')
plt.savefig('ab_test_pie_chart.png', transparent = 'True')
plt.savefig('ab_test_pie_chart.eps')

plt.show()


# ## Step 4: Who picks up an application?

# Recall that the sign-up process for MuscleHub has several steps:
# 1. Take a fitness test with a personal trainer (only Group A)
# 2. Fill out an application for the gym
# 3. Send in their payment for their first month's membership
# 
# Let's examine how many people make it to Step 2, filling out an application.
# 
# Start by creating a new column in `df` called `is_application` which is `Application` if `application_date` is not `None` and `No Application`, otherwise.

# In[13]:


df['is_application'] = df.apply(lambda row: 'No Application' if pd.isnull(row.application_date) else 'Application',    axis = 1)


# Now, using `groupby`, count how many people from Group A and Group B either do or don't pick up an application.  You'll want to group by `ab_test_group` and `is_application`.  Save this new DataFrame as `app_counts`

# In[14]:


app_counts = df.groupby(['ab_test_group', 'is_application']).email.count().reset_index()

print app_counts


# We're going to want to calculate the percent of people in each group who complete an application.  It's going to be much easier to do this if we pivot `app_counts` such that:
# - The `index` is `ab_test_group`
# - The `columns` are `is_application`
# Perform this pivot and save it to the variable `app_pivot`.  Remember to call `reset_index()` at the end of the pivot!

# In[15]:


app_pivot = pd.pivot_table(app_counts, index = 'ab_test_group', columns = 'is_application', values = 'email')    .reset_index()
    

print app_pivot


# Define a new column called `Total`, which is the sum of `Application` and `No Application`.

# In[16]:


app_pivot['Total'] = app_pivot['Application'] + app_pivot['No Application']

print app_pivot


# Calculate another column called `Percent with Application`, which is equal to `Application` divided by `Total`.

# In[17]:


app_pivot['Percent with Application'] = app_pivot['Application'] / app_pivot['Total']

print app_pivot


# It looks like more people from Group B turned in an application.  Why might that be?
# 
# We need to know if this difference is statistically significant.
# 
# Choose a hypothesis tests, import it from `scipy` and perform it.  Be sure to note the p-value.
# Is this result significant?

# In[18]:


from scipy.stats import chi2_contingency

#Extract contingengy table of frequencies from pivot table
app_contingency = app_pivot.as_matrix(columns=['Application','No Application'])

#Perform chi-squared test on contingency table and store output statistics
app_chi2, app_pval, app_dof, app_expected = chi2_contingency(app_contingency)

print app_pval


# ## Step 4: Who purchases a membership?

# Of those who picked up an application, how many purchased a membership?
# 
# Let's begin by adding a column to `df` called `is_member` which is `Member` if `purchase_date` is not `None`, and `Not Member` otherwise.

# In[19]:


df['is_member'] = df.apply(lambda row: 'Not Member' if pd.isnull(row.purchase_date) else 'Member', axis=1)


# Now, let's create a DataFrame called `just_apps` the contains only people who picked up an application.

# In[20]:


just_apps = df[df['is_application'] == 'Application']


# Great! Now, let's do a `groupby` to find out how many people in `just_apps` are and aren't members from each group.  Follow the same process that we did in Step 4, including pivoting the data.  You should end up with a DataFrame that looks like this:
# 
# |is_member|ab_test_group|Member|Not Member|Total|Percent Purchase|
# |-|-|-|-|-|-|
# |0|A|?|?|?|?|
# |1|B|?|?|?|?|
# 
# Save your final DataFrame as `member_pivot`.

# In[21]:


#Count members and non-members from each A/B group among people who picked up an application
member_counts = just_apps.groupby(['ab_test_group','is_member']).email.count().reset_index()
#Create pivot table
member_pivot = pd.pivot_table(member_counts, columns = 'is_member', index = 'ab_test_group', values = 'email').    reset_index()
#Add columns for total number of applications in each group and percent in each group who purchased a membership
member_pivot['Total'] = member_pivot['Member'] + member_pivot['Not Member']
member_pivot['Percent Purchase'] = member_pivot['Member'] / member_pivot['Total']

print member_pivot


# It looks like people who took the fitness test were more likely to purchase a membership **if** they picked up an application.  Why might that be?
# 
# Just like before, we need to know if this difference is statistically significant.  Choose a hypothesis tests, import it from `scipy` and perform it.  Be sure to note the p-value.
# Is this result significant?

# In[22]:


#Again, we use a chi-squared test of independence between group and membership (assuming application).
#First extract contingency table:
member_contingency = member_pivot.as_matrix(columns=['Member', 'Not Member'])

#Perform chi-squared test on contingency table and print p-value:
member_chi2, member_pval, member_dof, member_expected = chi2_contingency(member_contingency)

print member_pval


# Previously, we looked at what percent of people **who picked up applications** purchased memberships.  What we really care about is what percentage of **all visitors** purchased memberships.  Return to `df` and do a `groupby` to find out how many people in `df` are and aren't members from each group.  Follow the same process that we did in Step 4, including pivoting the data.  You should end up with a DataFrame that looks like this:
# 
# |is_member|ab_test_group|Member|Not Member|Total|Percent Purchase|
# |-|-|-|-|-|-|
# |0|A|?|?|?|?|
# |1|B|?|?|?|?|
# 
# Save your final DataFrame as `final_member_pivot`.

# In[23]:


#Again, follow the analogous steps as above.
final_member_counts = df.groupby(['ab_test_group', 'is_member']).email.count().reset_index()
final_member_pivot = pd.pivot_table(final_member_counts, index='ab_test_group', columns='is_member', values='email')    .reset_index()
final_member_pivot['Total'] = final_member_pivot['Member'] + final_member_pivot['Not Member']
final_member_pivot['Percent Purchase'] = final_member_pivot['Member'] / final_member_pivot['Total']

print final_member_pivot


# Previously, when we only considered people who had **already picked up an application**, we saw that there was no significant difference in membership between Group A and Group B.
# 
# Now, when we consider all people who **visit MuscleHub**, we see that there might be a significant different in memberships between Group A and Group B.  Perform a significance test and check.

# In[24]:


#Once again, implement the chi-squared test analogously.
final_member_contingency = final_member_pivot.as_matrix(columns=['Member', 'Not Member'])

final_member_chi2, final_member_pval, final_member_dof, final_member_expected =     chi2_contingency(final_member_contingency)
    
print final_member_pval


# ## Step 5: Summarize the acquisition funel with a chart

# We'd like to make a bar chart for Janet that shows the difference between Group A (people who were given the fitness test) and Group B (people who were not given the fitness test) at each state of the process:
# - Percent of visitors who apply
# - Percent of applicants who purchase a membership
# - Percent of visitors who purchase a membership
# 
# Create one plot for **each** of the three sets of percentages that you calculated in `app_pivot`, `member_pivot` and `final_member_pivot`.  Each plot should:
# - Label the two bars as `Fitness Test` and `No Fitness Test`
# - Make sure that the y-axis ticks are expressed as percents (i.e., `5%`)
# - Have a title

# In[25]:


#For all charts, we'll create a "group names" variable to use as the x-axis labels.
group_names = ['Fitness Test', 'No Fitness Test']

#Import percent formatter
from matplotlib.ticker import PercentFormatter

#The first chart will depict the percent of visitors who applied from each A/B group.
plt.bar(range(len(group_names)), app_pivot['Percent with Application'])

#Create ax object, set x-ticks to 0 and 1, and use "group names" variable to label x-ticks.
ax_app = plt.subplot()
ax_app.set_xticks(range(len(group_names)))
ax_app.set_xticklabels(group_names)

#Force y-axis to display values up to 20% and format y-tick labels as percentages.
ax_app.set_yticks([.02*k for k in range(11)])
ax_app.yaxis.set_major_formatter(PercentFormatter(xmax=1.0, decimals=0))

#Create title
plt.title('Percentage of Visitors Who Applied for Membership')

plt.savefig('app_rates.png')
plt.savefig('app_rates.eps')

plt.show()


# In[26]:


#Proceed analogously for percentage of applicants who purchase a membership.
plt.bar(range(len(group_names)), member_pivot['Percent Purchase'])

ax_member = plt.subplot()
ax_member.set_xticks(range(len(group_names)))
ax_member.set_xticklabels(group_names)

#Since the bars in the chart each have height approximately 80%, we set the y-axis to range from 0 to 1.
ax_member.set_yticks([0.1 * k for k in range(11)])
ax_member.yaxis.set_major_formatter(PercentFormatter(xmax=1.0, decimals=0))

plt.title('Percentage of Applicants Who Purchased a Membership')

plt.savefig('app_conversion_rates.png')
plt.savefig('app_conversion_rates.eps')

plt.show()


# In[27]:


#Proceed analogously for percentage of all visitors who purchase a membership.
plt.bar(range(len(group_names)), final_member_pivot['Percent Purchase'])

ax_final_member = plt.subplot()
ax_final_member.set_xticks(range(len(group_names)))
ax_final_member.set_xticklabels(group_names)

ax_final_member.set_yticks([.02 * k for k in range(11)])
ax_final_member.yaxis.set_major_formatter(PercentFormatter(xmax=1.0, decimals=0))

plt.title('Percentage of All Visitors Who Purchased a Membership')

plt.savefig('purchase_rates.png')
plt.savefig('purchase_rates.eps')

plt.show()

