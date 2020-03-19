import numpy as np
import pandas as pd
from LVChannelMap import LVmap
import datetime



class SlowControlAnalysis:
	def __init__( self ):
		self.data_df = None
		self.labview_time_offset = 2082844800
		self.datetime_values = None
		self.utc_to_pacific_offset = 8*60*60

	def AddSCDataFile( self, filename ):
		dat_array = np.genfromtxt( filename )

		if self.data_df is None:
			self.data_df = pd.DataFrame( data = dat_array, \
						columns = [LVmap[k] for k in range(0,35)] )
			print('\nFirst file loaded into dataframe.\n')
		else:
			new_data_df = pd.DataFrame( data = dat_array,\
						columns = [LVmap[k] for k in range(0,35)] )
			# for some reason, pd.concat is faster than DataFrame.append()
			df_list = [self.data_df,new_data_df]
			print('\nConcatenating new data to old DataFrame...\n')
			self.data_df = pd.concat(df_list)
			#print('Sorting by time...\n')
			self.data_df = self.data_df.sort_values('time [seconds]')
	
		self.datetime_values = []	
		for index,row in self.data_df.iterrows():
			self.datetime_values.append( datetime.datetime.utcfromtimestamp( row['time [seconds]'] - \
											self.labview_time_offset - \
											self.utc_to_pacific_offset))

		self.datetime_values = np.array(self.datetime_values)

		#start_date = datetime.datetime.utcfromtimestamp( self.data_df['time [seconds]'].iloc[0] - self.labview_time_offset )
		#end_date = datetime.datetime.utcfromtimestamp( self.data_df['time [seconds]'].iloc[-1] - self.labview_time_offset )
		print('\tData length: \t{} samples'.format(len(self.data_df)))
		print('\tData spans: \t{} to {}'.format(self.datetime_values[0],self.datetime_values[-1]))

	def SelectDataByDatetime( self, col_selection, start_time, end_time ): 
		# Selects data given a list of column names, or a single column name
		# given a start and end datetime
		if self.datetime_values is None:
			print('ERROR: datetimes for SC data have not yet been calculated. Have you added any data?')
			return
		if len(self.data_df) < 1:
			print('ERROR: SC data is empty!')
			return

		mask = ( self.datetime_values > start_time ) & \
			( self.datetime_values < end_time )

		sub_df = self.data_df[col_selection].loc[mask]
		sub_df['Datetime'] = self.datetime_values[mask]

		return sub_df

		#if isinstance(col_selection,list):
	def GetValueAtDatetime( self, col_selection, this_time ):
				
		if self.datetime_values is None:
			print('ERROR: datetimes for SC data have not yet been calculated. Have you added any data?')
			return
		if len(self.data_df) < 1:
			print('ERROR: SC data is empty!')
			return
		
		# Get the last point before the selected time
		idx = np.where(self.datetime_values < this_time)[0][-1]
		row = self.data_df.loc[ idx ]
		time_diff = this_time - self.datetime_values[ idx ]
		if time_diff.seconds > 60.:
			print('WARNING: the closest value is {:4.4} mins away from selection.'.format(time_diff.seconds/60.))

		return row[col_selection]
		
				




