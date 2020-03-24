from visualpic.data_reading.folder_scanners import (OsirisFolderScanner,
                                                   OpenPMDFolderScanner, 
                                                   HiPACEFolderScanner)
from visualpic.data_reading.field_readers import (OpenPMDFieldReader,
                                                 HiPACEFieldReader)
from visualpic.data_reading.particle_readers import HiPACEParticleReader
from visualpic.data_handling.data_container import DataContainer
from visualpic.visualization.vtk_visualizer import VTKVisualizer
from visualpic.ui.basic_render_window import BasicRenderWindow
import matplotlib.pyplot as plt
import numpy as np
import vtk
import time
import platform
import ctypes
import sys
from PyQt5 import QtWidgets
from PyQt5.Qt import Qt, QStyleFactory


def osiris_test():
    os_path = 'D:\\PhD\\Simulations_Data\\OSIRIS\\LimitationsPaper\\ene_sp-vs-gamma_0\\emitt-1\\100MeV\\MS'
    os_scanner = OsirisFolderScanner()
    fld_list = os_scanner.get_list_of_fields(os_path)
    sp_list = os_scanner.get_list_of_species(os_path)

    for field in fld_list:
        print(field.field_name)
    for species in sp_list:
        print(species.species_name)
        print(species.components_in_file)


def hipace_test():
    #file_path = 'M:\\beegfs\\desy\\group\\mpy\\ard\\ferran\\plasma_simulations\\HiPACE\\intrinsic_growth_paper\\ene_sp-vs-charge\\test_new_hp\\DATA\\density_driver_001340.0.h5'
    sim_path = 'M:\\beegfs\\desy\\group\\mpy\\ard\\ferran\\plasma_simulations\\HiPACE\\intrinsic_growth_paper\\ene_sp-vs-charge\\1pC_new\\DATA'
    #file_path = 'C:\\Users\\Angel\\ownCloud\\PhD\\Programming\\Python\\test_data\\HiPACE\\raw_witness_001340.0.h5'
    #hp_rd = HiPACEFieldReader()
    #fld, fld_md = hp_rd.read_field(file_path, 'EypBx', slice_i=0.5, slice_dir_i='z')
    #hp_pr = HiPACEParticleReader()
    #raw_data = hp_pr.read_particle_data(file_path, 'driver', component_list=['x', 'y', 'z'])
    #x, x_md = raw_data['x']
    #y, y_md = raw_data['y']
    #z, z_md = raw_data['z']
    #plt.hist2d(z, x, 100)
    #plt.show()
    hp_fs = HiPACEFolderScanner()
    fld_list = hp_fs.get_list_of_fields(sim_path)
    for field in fld_list:
        print(field.field_name)
        time_steps = field.timesteps
        #fld, fld_md = field.get_data(time_steps[100], slice_i=0.5, slice_dir_i='x')
        #plt.imshow(fld)
        #plt.show()
    sp_list = hp_fs.get_list_of_species(sim_path)
    for species in sp_list:
        print(species.species_name)
        time_steps = species.timesteps
        raw_data = species.get_data(time_steps[100], ['x', 'y', 'z'])
        x, x_md = raw_data['x']
        y, y_md = raw_data['y']
        z, z_md = raw_data['z']
        plt.hist2d(z, x, 100)
        plt.show()


    

def openpmd_test():
    file_path = 'D:\\PhD\\Simulations_Data\\FBPIC\\beam_dechirping\\final_cases\\a0_3-1e17-channel-10pC-final\\lab_diags\\hdf5\\data00000100.h5'
    opmd_fr = OpenPMDFieldReader()
    fld = opmd_fr.read_field(file_path, 'E/r')
    print(fld)


def openpmd_scanner_test():
    folder_path = 'D:\\PhD\\Simulations_Data\\FBPIC\\beam_dechirping\\final_cases\\a0_3-1e17-channel-10pC-final\\lab_diags\\hdf5'
    #folder_path = 'C:\\Users\\Angel\\ownCloud\\PhD\\Sample Data\\openPMD\\openPMD-example-datasets-draft\\example-3d\\hdf5'
    #folder_path = 'C:\\Users\\Angel\\ownCloud\\PhD\\Sample Data\\openPMD\\openPMD-example-datasets-draft\\example-2d\\hdf5'
    opmd_fs = OpenPMDFolderScanner()
    sp_list = opmd_fs.get_list_of_species(folder_path)
    for species in sp_list:
        print(species.species_name)
        time_steps = species.timesteps
        print(species.get_data(time_steps[0], ['x', 'px']))
    fld_list = opmd_fs.get_list_of_fields(folder_path)
    for field in fld_list:
        print(field.field_name)
        time_steps = field.timesteps
        print(field.get_data(time_steps[0]))


def openpmd_unit_conversion():
    folder_path = 'D:\\PhD\\Simulations_Data\\FBPIC\\beam_dechirping\\final_cases\\a0_3-1e17-channel-10pC-final\\lab_diags\\hdf5'
    #folder_path = 'C:\\Users\\Angel\\ownCloud\\PhD\\Sample Data\\openPMD\\openPMD-example-datasets-draft\\example-3d\\hdf5'
    #folder_path = 'C:\\Users\\Angel\\ownCloud\\PhD\\Sample Data\\openPMD\\openPMD-example-datasets-draft\\example-2d\\hdf5'
    opmd_fs = OpenPMDFolderScanner()
    sp_list = opmd_fs.get_list_of_species(folder_path)
    #for species in sp_list:
    #    print(species.species_name)
    #    time_steps = species.timesteps
    #    print(species.get_data(time_steps[0], ['x', 'px']))
    fld_list = opmd_fs.get_list_of_fields(folder_path)
    for field in fld_list:
        if field.field_name == 'Ex':
            time_steps = field.timesteps
            fld, md = field.get_data(time_steps[10])
            print(field.get_data(time_steps[10]))
            print(field.get_data(time_steps[10], field_units='T', time_units='fs', axes_units=['mm', 'mm'], axes_to_convert=['z', 'r']))


def osiris_unit_conversion():
    folder_path = 'D:\\PhD\\Simulations_Data\\OSIRIS\\LimitationsPaper\\ene_sp-vs-gamma_0\\emitt-1\\100MeV\\MS'
    #folder_path = 'D:\\PhD\\Simulations_Data\\OSIRIS\\LimitationsPaper\\ene_sp-vs-dens\\emitt-10\\1e17_for_movie_avg\\MS'
    os_fs = OsirisFolderScanner(plasma_density=7e23)
    sp_list = os_fs.get_list_of_species(folder_path)
    for species in sp_list:
        print(species.species_name)
        time_steps = species.timesteps
        #print(species.get_data(time_steps[0], ['x', 'px']))
        sp_data = species.get_data(time_steps[0], ['x', 'pz', 'q'], data_units=['SI', 'MeV/c', 'SI'])
        print(np.sum(sp_data['q'][0]))
    fld_list = os_fs.get_list_of_fields(folder_path)
    #for field in fld_list:
    #    if field.field_name == 'Ex':
    #        time_steps = field.timesteps
    #        #fld, md = field.get_data(time_steps[2])
    #        #print('')
    #        print(field.get_data(time_steps[2]))
    #        print(field.get_data(time_steps[2], field_units='SI', time_units='fs', axes_units=['mm', 'mm'], axes_to_convert=['z', 'x']))

def data_container_test():
    folder_path = 'D:\\PhD\\Simulations_Data\\OSIRIS\\LimitationsPaper\\ene_sp-vs-gamma_0\\emitt-1\\100MeV\\MS'
    #folder_path = 'D:\\PhD\\Simulations_Data\\OSIRIS\\LimitationsPaper\\ene_sp-vs-dens\\emitt-10\\1e17_for_movie_avg\\MS'
    #folder_path = 'D:\\PhD\\Simulations_Data\\OSIRIS\\EuPRAXIA\\workingPointTests\\5e16_selfGuiding_1pC_realLaser\\MS'
    sim_code = 'Osiris'
    plasma_density = 0.5e23
    dc = DataContainer(sim_code, folder_path, plasma_density)
    dc.load_data()
    print(dc.get_list_of_fields())
    print(dc.get_list_of_particle_species())
    Ez = dc.get_field('Ez')
    #I = dc.get_field('I')
    a = dc.get_field('a')
    time_steps = a.timesteps
    #fld, md = field.get_data(time_steps[2])
    #print('')
    #print(np.max(I.get_data(time_steps[0], field_units='W/m^2')[0]))
    a_data = a.get_data(time_steps[0])[0]
    print(a.get_only_metadata(time_steps[0]))
    print(np.max(a_data))
    ez_data = Ez.get_data(time_steps[0])[0]
    print(np.max(ez_data))
    #plt.imshow(a_data, aspect='auto')
    #plt.show()
    beam = dc.get_particle_species('witness-beam')
    print(beam.get_list_of_available_components())
    time_steps = beam.timesteps
    #print(species.get_data(time_steps[0], ['x', 'px']))
    sp_data = beam.get_data(time_steps[0], ['x', 'pz', 'q', 'x_prime'], data_units=['SI', 'MeV/c', 'SI', 'mrad'])
    print(sp_data)


def vtk_render_test():
    if platform.system() == 'Windows':
        myappid = 'visualpic' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        ctypes.windll.user32.SetProcessDPIAware() 
    # Enable scaling for high DPI displays
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setStyle(QStyleFactory.create('Fusion'))

    #folder_path = 'D:\\PhD\\Simulations_Data\\OSIRIS\\LimitationsPaper\\ene_sp-vs-gamma_0\\emitt-1\\100MeV\\MS'
    folder_path = 'D:\\PhD\\Simulations_Data\\OSIRIS\\LimitationsPaper\\ene_sp-vs-dens\\emitt-10\\1e17_for_movie_avg\\MS'
    #folder_path = 'D:\\PhD\\Simulations_Data\\OSIRIS\\EuPRAXIA\\workingPointTests\\5e16_selfGuiding_1pC_realLaser\\MS'
    sim_code = 'Osiris'
    plasma_density = 0.5e23
    dc = DataContainer(sim_code, folder_path, plasma_density)
    dc.load_data()
    print(dc.get_list_of_fields())
    plasma_dens = dc.get_field('rho', 'plasma')
    beam_dens = dc.get_field('rho', 'witness-beam')
    driver_dens = dc.get_field('rho', 'beam-driver')
    vis = VTKVisualizer()
    vis.add_field(plasma_dens, opacity='auto', cmap='Blues', vmax=0, vmin=-3, xtrim=[-1, 0])
    vis.add_field(beam_dens, opacity='linear negative', cmap='inferno')
    vis.add_field(driver_dens, opacity='linear negative', cmap='inferno')
    #vis.set_camera_angles(30, 10)
    #vis.set_camera_zoom(2)

    #time_steps = vis.get_possible_timesteps()
    #base_path = 'C:\\Users\\Angel\\Desktop\\vtk_tests\\'
    #for time_step in time_steps:
    #    file_path = base_path + 'fig_{}.png'.format(time_step)
    #    vis.render_to_file(time_step, file_path, resolution=[3000,1500], ts_is_index=False)

    vis.show(200)
    #vis.show(time_steps[100])
    print('a')


def vtk_render_test_2():
    folder_path = 'D:\\PhD\\Simulations_Data\\OSIRIS\\LimitationsPaper\\ene_sp-vs-gamma_0\\emitt-1\\100MeV\\MS'
    #folder_path = 'D:\\PhD\\Simulations_Data\\OSIRIS\\LimitationsPaper\\ene_sp-vs-dens\\emitt-10\\1e17_for_movie_avg\\MS'
    #folder_path = 'D:\\PhD\\Simulations_Data\\OSIRIS\\EuPRAXIA\\workingPointTests\\5e16_selfGuiding_1pC_realLaser\\MS'
    sim_code = 'Osiris'
    plasma_density = 0.5e23
    dc = DataContainer(sim_code, folder_path, plasma_density)
    dc.load_data()
    print(dc.get_list_of_fields())
    ez = dc.get_field('Ez')
    time_steps = ez.timesteps
    vis = VTKVisualizer()
    #vis.add_field(ez, opacity='V shape', cmap='RdBu', vmin=-0.4, vmax=0.4)
    vis.add_field(ez, vmin=-0.4, vmax=0.4)
    vis.show(time_steps[6])
    #vis.show(time_steps[100])
    print('a')


def vtk_render_test_3():
    #folder_path = 'D:\\PhD\\Simulations_Data\\OSIRIS\\LimitationsPaper\\ene_sp-vs-gamma_0\\emitt-1\\100MeV\\MS'
    folder_path = 'D:\\PhD\\Simulations_Data\\OSIRIS\\LimitationsPaper\\ene_sp-vs-dens\\emitt-10\\1e17_for_movie_avg\\MS'
    #folder_path = 'D:\\PhD\\Simulations_Data\\OSIRIS\\EuPRAXIA\\workingPointTests\\5e16_selfGuiding_1pC_realLaser\\MS'
    sim_code = 'Osiris'
    plasma_density = 0.5e23
    dc = DataContainer(sim_code, folder_path, plasma_density)
    dc.load_data()
    print(dc.get_list_of_fields())
    plasma_dens = dc.get_field('rho', 'plasma')
    beam_dens = dc.get_field('rho', 'witness-beam')
    driver_dens = dc.get_field('rho', 'beam-driver')
    time_steps = plasma_dens.timesteps
    vis = VTKVisualizer(background='white')
    vis.add_field(plasma_dens, opacity='auto', cmap='Blues', vmax=0, vmin=-3)
    vis.add_field(beam_dens, opacity='auto', cmap='inferno', vmax=0, vmin=-3)
    vis.add_field(driver_dens, opacity='auto', cmap='inferno', vmax=0, vmin=-3)
    base_path = 'C:\\Users\\Angel\\Desktop\\vtk_tests\\'
    for time_step in time_steps:
        file_path = base_path + 'fig_{}.png'.format(time_step)
        vis.render_to_file(time_step, file_path, resolution=[3000,1500])
    vis.show(time_steps[100])
    #vis.show(time_steps[3])
    #vis.show(time_steps[100])
    #print('a')


def vtk_render_test_opmd():
    #if platform.system() == 'Windows':
    #    myappid = 'visualpic' # arbitrary string
    #    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    #    ctypes.windll.user32.SetProcessDPIAware() 
    ## Enable scaling for high DPI displays
    #QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    #QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    #QtWidgets.QApplication.setStyle(QStyleFactory.create('Fusion'))
    #folder_path = 'C:\\Users\\Angel\\ownCloud\\PhD\\Sample Data\\openPMD\\openPMD-example-datasets-draft\\example-3d\\hdf5\\'
    folder_path = 'C:\\Users\\Angel\\ownCloud\\PhD\\Sample Data\\openPMD\\openPMD-example-datasets-draft\\example-thetaMode\\hdf5\\'

    #folder_path = 'D:\\PhD\\Simulations_Data\\FBPIC\\beam_dechirping\\final_cases\\a0_3-1e17-channel-10pC-final\\lab_diags\\hdf5'
    #folder_path = 'F:\\PhD\\Simulations_Data\\multistage_eupraxia_design\\final_cases\\smoothed_0p3micron_4m_centered\\1_first_plasma\\lab_diags\\hdf5'
    #folder_path = 'F:\\PhD\\Simulations_Data\\multistage_eupraxia_design\\final_cases\\smoothed_0p3micron_4m_centered\\1_first_plasma_for_plot\\lab_diags\\hdf5'
    sim_code = 'openPMD'
    dc = DataContainer(sim_code, folder_path)
    dc.load_data()
    print(dc.get_list_of_fields())
    rho = dc.get_field('rho')
    ez = dc.get_field('Ez')
    er = dc.get_field('Er')
    jz = dc.get_field('Jz')
    vis = VTKVisualizer()
    #vis.set_background('black', [0.12, 0.3, 0.475]) #[0, 57/255, 138/255])
    #print(vis.set_color_window(-1))
    #print(vis.set_color_level(1000))
    #vis.set_brightness(0.7)
    #vis.set_contrast(0.5)
    #print(vis.get_contrast())
    #print(vis.get_brightness())
    #vis.set_brightness(-0.5)
    #vis.add_field(rho)
    vis.add_field(jz)
    #vis.add_field(ez)
    #vis.add_field(er)
    #vis.add_field(rho, xtrim=[-0.3, 0.3], ytrim=[-0.3, 0.3], resolution=[100,100,100])
    #vis.add_field(rho, xtrim=[-0.3, 0.3], ytrim=[-0.3, 0.3])
    t1 = time.time()
    vis.show(-1)
    print(time.time() - t1)
    #vis.show(time_steps[100])
    #base_path = 'C:\\Users\\Angel\\Desktop\\vtk_tests\\'
    #time_steps = vis.get_possible_timesteps()
    #for time_step in time_steps:
    #    file_path = base_path + 'fig_{}.png'.format(time_step)
    #    vis.render_to_file(time_step, file_path, resolution=[3000,1500], ts_is_index=False)

    #vis = VTKVisualizer()
    ##vis.add_field(ez, opacity='V shape', cmap='RdBu', vmin=-0.4, vmax=0.4)
    #print('ss')
    #vis.add_field(rho, xtrim=[-0.3, 0.3], ytrim=[-0.3, 0.3])
    ##vis.add_field(rho, xtrim=[-0.3, 0.3], ytrim=[-0.3, 0.3])
    #t1 = time.time()
    ##vis.show(time_steps[200])
    #print(time.time() - t1)
    #print('a')

   
    #vis.interactor.Start()

def test_qt_window():
    if platform.system() == 'Windows':
        myappid = 'visualpic' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        ctypes.windll.user32.SetProcessDPIAware() 
    # Enable scaling for high DPI displays
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setStyle(QStyleFactory.create('Fusion'))

    folder_path = 'C:\\Users\\Angel\\ownCloud\\PhD\\Sample Data\\openPMD\\openPMD-example-datasets-draft\\example-3d\\hdf5\\'
    sim_code = 'openPMD'
    dc = DataContainer(sim_code, folder_path)
    dc.load_data()
    print(dc.get_list_of_fields())
    rho = dc.get_field('Ez')
    time_steps = rho.timesteps

    vis = VTKVisualizer()
    vis.add_field(rho)
    app = QtWidgets.QApplication(sys.argv)
    window = BasicRenderWindow(vis)
    app.exec_()


#vtk_render_test_opmd()
#vtk_render_test_3()
#test_qt_window()
#vtk_render_test()
vtk_render_test_opmd()
