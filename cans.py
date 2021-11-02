import numpy as np
from IPython import display

from config import grains
from config import brewing_setup as bs
from config import beer_colors as bc

class Cans:

    def __init__(self, beer_style, batch_size_gal, boil_time_min, mash_temperature_f, grain_temperature_f = 64.0):
        self.beer_style = beer_style
        self.batch_size_gal = batch_size_gal
        self.mash_temperature_f = mash_temperature_f
        self.grain_temperature_f = grain_temperature_f
        self.boil_time_min = boil_time_min

    def add_grains(self, name, weight_lb):
        if hasattr(self, 'added_grains'):
            self.added_grains[name] = {'weight': weight_lb, 'points': grains[name]['points'] * weight_lb, 'color': grains[name]['lovibond'] * weight_lb}
        else:
            self.added_grains = {name: {'weight': weight_lb, 'points': grains[name]['points'] * weight_lb, 'color': grains[name]['lovibond'] * weight_lb}}

        print(f"Adding {weight_lb} lb(s) of {name} to mash bill")
        
    def calculate_brewing(self):
        total_grain_weight_lb = sum([self.added_grains[k]['weight'] for k in self.added_grains])
        print(f"Total grain weight is {total_grain_weight_lb} lbs")
        total_points = sum([self.added_grains[k]['points'] for k in self.added_grains])
        print(f"Target original gravity is {round((1 + (0.001*total_points*bs['efficiency']/self.batch_size_gal)), 3)}\n")
        
        for k in self.added_grains:
            print(f"{self.added_grains[k]['weight']} lb(s) of {k} ({round((100.*self.added_grains[k]['weight']/total_grain_weight_lb), 1)}%)")

        # The 0.04 accounts for the density change from boiling to yeast-pitching temperatures
        volume_before_wort_chill_gal = self.batch_size_gal / (1.0-0.04)

        # The 60 converts boil time in minutes to hours
        volume_before_boil_gal = volume_before_wort_chill_gal + bs['boil_pot_loss_gal'] + (bs['boil_evaporation_rate_gal_per_h'] * self.boil_time_min / 60.)

        mash_thickness = 4.*(volume_before_boil_gal + (bs['grain_absorption_gal_per_lb']*total_grain_weight_lb) \
                        + bs['mash_tun_loss_gal']) / total_grain_weight_lb

        water_volume = 0.25 * mash_thickness * total_grain_weight_lb
        print(f"\nStrike water volume is {round(water_volume, 1)} gallons")

        total_mash_volume = bs['mash_tun_loss_gal'] + 0.25 * total_grain_weight_lb \
            * (1.3125 + mash_thickness - 1.)

        print(f"Total mash volume is {round(total_mash_volume, 1)} gallons")
        print(f"Boil volume is {round(volume_before_boil_gal, 1)} gallons")

        total_grain_weight_kg = total_grain_weight_lb * 0.45359237
        # 979 is water density in kg/m^-3 at 153.5 F
        water_weight_kg = 979.0 * mash_thickness * total_grain_weight_lb * 0.000946352946
        mash_temperature_k = 273.15 + (self.mash_temperature_f-32.0)*5.0/9.0
        grain_temperature_k = 273.15 + (self.grain_temperature_f-32.0)*5.0/9.0
        water_temperature_k = mash_temperature_k + (((0.3822*total_grain_weight_kg)/water_weight_kg)*(mash_temperature_k-grain_temperature_k))
        water_temperature_f = (water_temperature_k-273.15)*9.0/5.0 + 32.0

        print(f"Strike water temperature is {round(water_temperature_f, 1)} F")
        
    def calculate_color(self):
        """Colors come from homebrewing.org, used for educational purposes only"""
        
        total_color_units = sum([self.added_grains[k]['color'] for k in self.added_grains]) / self.batch_size_gal
        srm = 1.4922 * total_color_units**0.6859
        print(f"\nSRM is {round(srm,0)}, beer color will be approximately:")
        self.srm = int(srm)
        if(self.srm in bc):
            img = './img/srm_' + str(self.srm).zfill(2) + '.jpg'
        else:
            index = np.searchsorted(bc, self.srm) - 1
            if index < 0:
                index = 0
            img = './img/srm_' + str(bc[index]).zfill(2) + '.jpg'
        return img

