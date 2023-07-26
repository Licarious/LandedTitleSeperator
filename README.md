# LandedTitleSeperator
 Tool for merging and spiting CK3 landed titles files
 
 Use:
 1. Drop your landed_title folder into _Input folder
 2. Run LandedTitleSeperator.py
 3. Extract landed_title back to your mod.
 
 Advanced options:
	
 	Main:
  		file_name_restriction a list of any landed title files that you don't want to add new holdings from

	parse_landed_titles3 arguments:
		editOnly: if True will only edit values from the landed_titles file without adding new holdings to the landed_titles dictionary
		overwriteSimilar: if True will overwrite values in mergeMulti list if the holding is found again and contains lines with same key
		restrictedLines: list of lines that will not be updated if they are set and the holding is found again 
