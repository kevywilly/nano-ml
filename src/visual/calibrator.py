# https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
# https://github.com/bvnayak/stereo_calibration
# https://learnopencv.com/making-a-low-cost-stereo-camera-using-opencv/

from uuid import uuid1
import os
from settings import settings
import cv2 as cv
import numpy as np
from src.visual.camera_model import CameraModel

LEFT = 0
RIGHT = 1

COLS = 8
ROWS = 5

class Calibrator:

    def __init__(self):
        self.stereo_count = 0
        self.left_count = 0
        self.right_count = 0

        self.image_output_folder = f"{settings.calibration_folder}/images/output"
        self.stereo_right_folder = f"{settings.calibration_folder}/images/stereo/right"
        self.stereo_left_folder = f"{settings.calibration_folder}/images/stereo/left"
        self.calibration_model_folder = settings.calibration_model_folder
        self.calibration_3d_map_file = settings.calibration_3d_map_file
        self.calibration_rectification_model_file = settings.calibration_rectification_model_file
        self.calibration_camera_model_file = settings.calibration_camera_model_file

        self._make_folder(self.stereo_right_folder)
        self._make_folder(self.stereo_left_folder)
        self._make_folder(self.image_output_folder)
        self._make_folder(self.calibration_model_folder)
        
        self._get_counts()

        self.w = settings.cam_width
        self.h = settings.cam_height

        self.objpoints = [] # 3d point in real world space
        self.imgpoints_l = []
        self.imgpoints_r = []

        self.objp = np.zeros((COLS*ROWS,3), np.float32)
        self.objp[:,:2] = np.mgrid[0:ROWS,0:COLS].T.reshape(-1,2)

    def _make_folder(self, folder):
        try:
            os.makedirs(folder)
        except FileExistsError:
            pass
        except Exception as ex:
            print(ex)
            raise ex

    def _get_counts(self):
        self.stereo_count = self._get_count(self.stereo_left_folder)
        self.right_count = 0
        self.left_count = 0

    def _get_count(self, folder):
        return len(os.listdir(folder))
    
    def _write_image(self, image, folder: str, filename: str):
        pth = os.path.join(folder, filename)
        cv.imwrite(pth, img=image)

    def _generate_filenamne(self):
        return f"{str(uuid1())}.png"
    
    def collect_stereo(self, image_right, image_left) -> int:
        print("collecting stereo")
        filename = self._generate_filenamne()
        self._write_image(image_right, self.stereo_right_folder, filename)
        self._write_image(image_left, self.stereo_left_folder, filename)
        self.stereo_count = self.stereo_count + 1
        return self.stereo_count

    def _get_image_filenames(self):
        left = os.listdir(self.stereo_left_folder)
        right = os.listdir(self.stereo_right_folder)
        return [(left[i],right[i])for i in range(0, len(left))]
        

    def _get_stereo_filenames(self):
        filenames_l = os.listdir(self.stereo_left_folder)
        filenames_r = os.listdir(self.stereo_right_folder)
        filenames_l.sort()
        filenames_r.sort()
        return filenames_l, filenames_r
    
    def _read_stereo(self, filename):
        return (
            cv.imread(os.path.join(self.stereo_left_folder,filename)), 
            cv.imread(os.path.join(self.stereo_right_folder,filename))
        )
    
    def calibrate(self):
        
        filenames_l, filenames_r = self._get_stereo_filenames()

        print(f'found {len(filenames_l)} files for Left Camera')
        print(f'found {len(filenames_r)} files for Right Camera')
    
        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        
        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        
        found_corners = False
        for _, filename in enumerate(filenames_l):

            img_l, img_r = self._read_stereo(filename)

            gray_l = cv.cvtColor(img_l, cv.COLOR_BGR2GRAY)
            gray_r = cv.cvtColor(img_r, cv.COLOR_BGR2GRAY)

            ret_l, corners_l = cv.findChessboardCorners(gray_l, (ROWS,COLS), None)
            ret_r, corners_r = cv.findChessboardCorners(gray_r, (ROWS,COLS), None)

            # If found, add object points, image points (after refining them)
            self.objpoints.append(self.objp)
            
            if ret_l == True:
                found_corners = True
                rt = cv.cornerSubPix(gray_l, corners_l, (11,11), (-1,-1), criteria)
                self.imgpoints_l.append(corners_l)

                # Draw and display the corners
                cv.drawChessboardCorners(img_l, (ROWS,COLS), corners_l, ret_l)
                cv.imwrite(os.path.join(self.image_output_folder, f"cap_left_{filename}"), img_l)
                # cv.imshow('img', img)
                # cv.waitKey(500)

            if ret_r == True:
                found_corners = True
                rt = cv.cornerSubPix(gray_r, corners_r, (11,11), (-1,-1), criteria)
                self.imgpoints_r.append(corners_r)

                # Draw and display the corners
                cv.drawChessboardCorners(img_r, (ROWS,COLS), corners_r, ret_r)
                cv.imwrite(os.path.join(self.image_output_folder, f"cap_right_{filename}"), img_r)
                # cv.imshow('img', img)
                # cv.waitKey(500)

        if not found_corners:  
            print("No corners found...")
            return  
                
        print("Calibrating camera")

        img_shape = gray_l.shape[::-1]

        rt1, self.M1, self.d1, self.r1, self.t1 = cv.calibrateCamera(
            self.objpoints, self.imgpoints_l, img_shape, None, None
            )
        
        rt2, self.M2, self.d2, self.r2, self.t2 = cv.calibrateCamera(
            self.objpoints, self.imgpoints_r, img_shape, None, None
            )
        
        print(f'Left Camera\n==============================')
        print(f'Left rmse:', {rt1})
        print(f'Left matrix left:\n {self.M1}')
        print(f'Left distortion coeffs:\n {self.d1}')

        print(f'Right Camera\n==============================')
        print(f'Right rmse:', {rt2})
        print(f'Right matrix:\n {self.M2}')
        print(f'Right distortion coeffs:\n {self.d2}')

        self.save_rectified_images(img_shape)
        return self.stereo_calibrate(img_shape)


    def save_rectified_images(self,dims):
            
        
            print("saving rectified images")

            filenames_l, filenames_r = self._get_stereo_filenames()

            newcameramtx_l, roi_l = cv.getOptimalNewCameraMatrix(self.M1, self.d1, dims, 1, dims)
            newcameramtx_r, roi_r = cv.getOptimalNewCameraMatrix(self.M2, self.d2, dims, 1, dims)
            
            for idx, filename in enumerate(filenames_l):
        
                # get new camera matrix
                img_l, img_r = self._read_stereo(filename)

                dst_l = cv.undistort(img_l, self.M1, self.d1, None, newcameramtx_l)
                # crop the image
                x, y, w, h = roi_l
                dst_l = dst_l[y:y+h, x:x+w]

                dst_r = cv.undistort(img_r, self.M2, self.d2, None, newcameramtx_r)
                # crop the image
                x, y, w, h = roi_r
                dst_r = dst_r[y:y+h, x:x+w]
        

                cv.imwrite(os.path.join(self.image_output_folder, f"cap_left_rectified_{filename}"), dst_l)
                cv.imwrite(os.path.join(self.image_output_folder, f"cap_right_rectified_{filename}"), dst_r)
            
        
    def stereo_calibrate(self, dims):
        print(f"dims: {dims}")
        flags = 0
        flags |= cv.CALIB_FIX_INTRINSIC
        # flags |= cv.CALIB_FIX_PRINCIPAL_POINT
        flags |= cv.CALIB_USE_INTRINSIC_GUESS
        flags |= cv.CALIB_FIX_FOCAL_LENGTH
        # flags |= cv.CALIB_FIX_ASPECT_RATIO
        flags |= cv.CALIB_ZERO_TANGENT_DIST
        # flags |= cv.CALIB_RATIONAL_MODEL
        # flags |= cv.CALIB_SAME_FOCAL_LENGTH
        # flags |= cv.CALIB_FIX_K3
        # flags |= cv.CALIB_FIX_K4
        # flags |= cv.CALIB_FIX_K5

        stereocalib_criteria = (cv.TERM_CRITERIA_MAX_ITER +
                                cv.TERM_CRITERIA_EPS, 100, 1e-5)
        ret, M1, d1, M2, d2, R, T, E, F = cv.stereoCalibrate(
            self.objpoints, self.imgpoints_l,
            self.imgpoints_r, self.M1, self.d1, self.M2,
            self.d2, dims,
            criteria=stereocalib_criteria, flags=flags)

        print('Intrinsic_mtx_1', M1)
        print('dist_1', d1)
        print('Intrinsic_mtx_2', M2)
        print('dist_2', d2)
        print('R', R)
        print('T', T)
        print('E', E)
        print('F', F)

        print(f"Saving rectify params ...... {self.calibration_rectification_model_file}")
      
        cv_file = cv.FileStorage(self.calibration_camera_model_file, cv.FILE_STORAGE_WRITE)
        cv_file.write("M1",M1)
        cv_file.write("dist1",d1)
        cv_file.write("M2",M2)
        cv_file.write("dist2",d2)
        cv_file.write("R",R)
        cv_file.write("T",T)
        cv_file.write("E",E)
        cv_file.write("F",F)
        cv_file.release()

        self.camera_model = CameraModel(
            M1 = M1, M2 = M2, dist1 = self.d1, dist2 = self.d2, rvecs1 = self.r1, rvecs2 = self.r2, R = R, T = T, E = E, F = F
        )
        
        print(" ")
        print(self.camera_model.dict())

        cv.destroyAllWindows()
        return self.camera_model
        
    """
    def map_all_3d(self, map11, map12, map21, map22):

        cv_file = cv.FileStorage(settings.calibration_3d_map_file, cv.FILE_STORAGE_READ)
        cv_file
        
        m11=cv_file.getNode("left_map_1").mat()
        m12=cv_file.getNode("left_map_2").mat()
        m21=cv_file.getNode("right_map_1").mat()
        m22=cv_file.getNode("right_map_2").mat()

        cv_file.release()
        
        assert m11 == map11
        
        

        for filename in os.listdir(settings.calibration_stereo_left_folder):
            img_l = cv.imread(os.path.join(settings.calibration_stereo_left_folder,filename))
            img_r = cv.imread(os.path.join(settings.calibration_stereo_right_folder,filename))

            mapped_l = cv.remap(img_l, map11, map21, cv.INTER_LANCZOS4)
            mapped_r = cv.remap(img_r, map12, map22, cv.INTER_LANCZOS4)
 
        
            out = mapped_r.copy()
       
            out[:,:,0] = mapped_r[:,:,0]
            out[:,:,1] = mapped_r[:,:,1]
            out[:,:,2] = mapped_l[:,:,2]

            cv.imwrite(os.path.join(settings.calibration_image_output_folder, f"3d_{filename}"),out)
    """
    

    def rectify3d(self, model: CameraModel):

        filenames, _ = self._get_stereo_filenames()

        filename = filenames[0]

        img_l, img_r = self._read_stereo(filename)
        gray_l = cv.cvtColor(img_l, cv.COLOR_BGR2GRAY)
        
        (h,w) = img_l.shape[:2]
        
        rectify_scale = 0.94

        R1, R2, P1, P2, Q, roi1, roi2 = cv.stereoRectify(
            model.M1, 
            model.dist1, 
            model.M2, 
            model.dist2, 
            (w,h),
            model.R,
            model.T,
            rectify_scale,
            (0,0)
            )
        
        print(f"Saving rectify params ...... {self.calibration_rectification_model_file}")
      
        cv_file = cv.FileStorage(self.calibration_rectification_model_file, cv.FILE_STORAGE_WRITE)
        cv_file.write("R1",R1)
        cv_file.write("R2",R2)
        cv_file.write("P1",P1)
        cv_file.write("P2",P2)
        cv_file.write("Q",Q)
        cv_file.write("roi1",roi1)
        cv_file.write("roi2",roi2)
        cv_file.release()

        left_map_1, left_map_2 = cv.initUndistortRectifyMap(
            model.M1, 
            model.dist1, 
            R1, 
            P1, 
            gray_l.shape[::-1], 
            m1type=5
            )

        right_map_1, right_map_2 = cv.initUndistortRectifyMap(
            model.M2, 
            model.dist2, 
            R2,
            P2, 
            gray_l.shape[::-1], 
            m1type=5
            )
        
        print(f"Saving 3dmapping paraeters ...... {self.calibration_3d_map_file}")
      
        cv_file = cv.FileStorage(self.calibration_3d_map_file, cv.FILE_STORAGE_WRITE)
        cv_file.write("left_map_1", left_map_1)
        cv_file.write("left_map_2",left_map_2)
        cv_file.write("right_map_1",right_map_1)
        cv_file.write("right_map_2",right_map_2)
        cv_file.release()
        
        
        mapped_l = cv.remap(img_l, left_map_1, left_map_2, cv.INTER_LANCZOS4)
        mapped_r = cv.remap(img_r, right_map_1, right_map_2, cv.INTER_LANCZOS4)
 
        
        out = mapped_r.copy()
       
        out[:,:,0] = mapped_r[:,:,0]
        out[:,:,1] = mapped_r[:,:,1]
        out[:,:,2] = mapped_l[:,:,2]


        cv.imwrite(os.path.join(self.image_output_folder, f"out_{filename}"), out)
        cv.imwrite(os.path.join(self.image_output_folder, f"left_{filename}"), mapped_l)
        cv.imwrite(os.path.join(self.image_output_folder, f"right_{filename}"), mapped_r)


        window_size = 3
        min_disp = 16
        num_disp = 112-min_disp
       
        stereo = cv.StereoSGBM_create(minDisparity = min_disp,
            numDisparities = num_disp,
            blockSize = 16,
            P1 = 8*3*window_size**2,
            P2 = 32*3*window_size**2,
            disp12MaxDiff = 1,
            uniquenessRatio = 10,
            speckleWindowSize = 100,
            speckleRange = 32
        )

        
        print('computing disparity...')

        gray_l = cv.cvtColor(mapped_l, cv.COLOR_BGR2GRAY)
        gray_r = cv.cvtColor(mapped_r, cv.COLOR_BGR2GRAY)

        disp = stereo.compute(gray_l, gray_r).astype(np.float32) / 16.0

        print('generating 3d point cloud...',)
        #h, w = mapped_l.shape[:2]
        #f = 0.8*w                          # guess for focal length
        #Q = np.float32([[1, 0, 0, -0.5*w],
        #                [0,-1, 0,  0.5*h], # turn points 180 deg around x-axis,
        #                [0, 0, 0,     -f], # so that y-axis looks up
        #                [0, 0, 1,      0]])
        #points = cv.reprojectImageTo3D(disp, Q)
        #colors = cv.cvtColor(imgL, cv.COLOR_BGR2RGB)
        #mask = disp > disp.min()
        #out_points = points[mask]
        #out_colors = colors[mask]
        #out_fn = 'out.ply'
        #write_ply(out_fn, out_points, out_colors)
        #print('%s saved' % out_fn)

        #cv.imshow('left', imgL)
        #cv.imshow('disparity', (disp-min_disp)/num_disp)
        #cv.waitKey()

        #cv.imwrite(os.path.join(self.image_output_folder, f"disp_1{filename}"), (disp-min_disp)/num_disp)
        cv.imwrite(os.path.join(self.image_output_folder, f"disp_2{filename}"), disp)
        
        print('Done')




