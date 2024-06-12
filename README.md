# Fuzzy Logic project 2024

## Motivation

Since I have grown up on a farm and have some experience in farming, I thought I could use my studies to help my
father by creating a model that could predict crop yield on data on the climate and fertility of soil.
This information could help maximize profits and also maybe see, how climate change has impacted our lively-hood.


## Dataset

Link to dataset: https://huggingface.co/datasets/CropNet/CropNet (Google Drive link in the document).
For this code I used the WRF_HRRR 2022 Oregon dataset.

Also to compare the generated yield to the actual ones, I used the USDA winter wheat 2022 dataset. (also found at CropNet)

The inital idea was to create a model that could take as an input fertility of soil,
sunlight, rainfall, temperature, the type of crop planted and return the crop yield in hectares.
 
Since I couldn't find datasets that had all of this information, plus the resulting project would have become too
massive for one person to manage, I decided to only use 
'Avg Temperature (K)', 'Precipitation (kg m^-2)', 'Relative Humidity (%)' and 'Vapor Pressure Deficit (kPa)'
to calculate the crop yield.


## Technical

I have opted to use the Mamdani-fuzzy inference system for my project, because this model seemed the most 
graspable during my studies for this course.

I used the scikit-fuzzy package in my code (https://pythonhosted.org/scikit-fuzzy/overview.html), because this enables us
to easily implement the selected system.

## Rules

I've decided that the crop yield will show the average tons per hectare for winter wheat, because this is the culture that
we grow mostly on my family farm.


## Ideas for expansion

I could create different rulesets for different crops. Also, more parameters could be added to maximize the accuracy
of the system.


## References

https://pulsegrow.com/blogs/learn/vpd

https://eos.com/blog/growing-wheat/

https://huggingface.co/datasets/CropNet/CropNet

https://pythonhosted.org/scikit-fuzzy/overview.html

