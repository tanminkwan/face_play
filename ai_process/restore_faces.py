import cv2
import torch
from torchvision.transforms.functional import normalize
from codeformer.basicsr.utils import img2tensor, tensor2img
from codeformer.facelib.utils.face_restoration_helper import FaceRestoreHelper
from codeformer.basicsr.utils.registry import ARCH_REGISTRY

class FaceRestorer:
    """
    얼굴 복원을 위한 클래스
    한 번 초기화하고 여러 이미지에 재사용 가능
    """
    def __init__(self, model_path, use_gpu=False):
        """
        FaceRestorer 클래스 초기화
        
        :param model_path: CodeFormer 모델 파일 경로
        :param use_gpu: GPU 사용 여부 (기본값: False)
        """
        self.model_path = model_path
        self.device = 'cuda' if use_gpu and torch.cuda.is_available() else 'cpu'
        self.use_gpu = use_gpu
        
        # 모델 로드
        self.model = ARCH_REGISTRY.get('CodeFormer')(
            dim_embd=512, 
            codebook_size=1024, 
            n_head=8, 
            n_layers=9, 
            connect_list=['32', '64', '128', '256']
        ).to(self.device)
        
        checkpoint = torch.load(model_path, weights_only=True, map_location=self.device)['params_ema']
        self.model.load_state_dict(checkpoint)
        self.model.eval()
        
        # Face Helper 초기화
        self.face_helper = FaceRestoreHelper(
            upscale_factor=1,
            face_size=512,
            crop_ratio=(1, 1),
            det_model='retinaface_resnet50',
            save_ext='png',
            use_parse=True,
            device=self.device
        )
        
        print(f"FaceRestorer initialized using device: {self.device}")
    
    def restore(self, input_image, w=0.5, only_center_face=False):
        """
        입력 이미지의 얼굴을 복원
        
        :param input_image: ndarray 타입의 입력 이미지
        :param w: 복원 강도 가중치 (0~1, 기본값: 0.5)
        :param only_center_face: 중앙 얼굴만 처리할지 여부
        :return: ndarray 타입의 복원된 이미지
        """
        # 이미지 크기 저장
        h, w_img, _ = input_image.shape
        
        # Face Helper 초기화
        self.face_helper.clean_all()
        self.face_helper.read_image(input_image)
        self.face_helper.get_face_landmarks_5(
            only_center_face=only_center_face, 
            resize=512, 
            eye_dist_threshold=5
        )
        self.face_helper.align_warp_face()
        
        # 얼굴 복원
        for idx, cropped_face in enumerate(self.face_helper.cropped_faces):
            cropped_face_t = img2tensor(cropped_face / 255., bgr2rgb=True, float32=True).to(self.device)
            normalize(cropped_face_t, (0.5, 0.5, 0.5), (0.5, 0.5, 0.5), inplace=True)
            cropped_face_t = cropped_face_t.unsqueeze(0).to(self.device)
            
            try:
                with torch.no_grad():
                    output = self.model(cropped_face_t, w=w, adain=True)[0]
                    restored_face = tensor2img(output, rgb2bgr=True, min_max=(-1, 1))
                del output
                if self.use_gpu:
                    torch.cuda.empty_cache()
            except RuntimeError as error:
                print(f'Error: {error}')
                print('If you encounter CUDA out of memory, try to set --tile with a smaller number.')
            else:
                restored_face = restored_face.astype('uint8')
                self.face_helper.add_restored_face(restored_face)
        
        # 결과 생성
        self.face_helper.get_inverse_affine(None)
        restored_img = self.face_helper.paste_faces_to_input_image()
        
        # 최종 이미지 크기 조정 (원본 크기로)
        restored_img = cv2.resize(restored_img, (w_img, h))
        
        return restored_img
    
    def __del__(self):
        """소멸자: 리소스 정리"""
        if self.use_gpu:
            torch.cuda.empty_cache()

# 사용 예시
if __name__ == "__main__":
    # 모델 한 번만 로드
    restorer = FaceRestorer(model_path="C:\\models\\codeformer-v0.1.0.pth", use_gpu=True)
    
    # 여러 이미지 처리
    img1 = cv2.imread("cap1.jpg")
    restored_img1 = restorer.restore(img1)
    cv2.imwrite('output1.jpg', restored_img1)
    
    img2 = cv2.imread("cap2.jpg")
    restored_img2 = restorer.restore(img2)
    cv2.imwrite('output2.jpg', restored_img2)
    
    img3 = cv2.imread("cap3.jpg")
    restored_img3 = restorer.restore(img3)
    cv2.imwrite('output3.jpg', restored_img3)