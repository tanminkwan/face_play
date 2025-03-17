import cv2
import torch
from torchvision.transforms.functional import normalize
from codeformer.basicsr.utils import img2tensor, tensor2img
from codeformer.facelib.utils.face_restoration_helper import FaceRestoreHelper
from codeformer.basicsr.utils.registry import ARCH_REGISTRY

def restore_face(input_image, use_gpu=False):
    """
    얼굴 복원 함수
    
    :param input_image: ndarray 타입의 입력 이미지
    :param model_path: CodeFormer 모델 파일 경로
    :param use_gpu: GPU 사용 여부 (기본값: False)
    :return: ndarray 타입의 복원된 이미지
    """
    # 모델 로드
    #device = torch.device('cuda' if use_gpu and torch.cuda.is_available() else 'cpu')
    device = 'cuda' if use_gpu and torch.cuda.is_available() else 'cpu'
    model = ARCH_REGISTRY.get('CodeFormer')(dim_embd=512, codebook_size=1024, n_head=8, n_layers=9, connect_list=['32', '64', '128', '256']).to(device)
    
    checkpoint = torch.load(CODEFORMER_MODEL, weights_only=True, map_location=device)['params_ema']
    model.load_state_dict(checkpoint)
    model.eval()

    # 이미지 크기 저장
    h, w, _ = input_image.shape

    # 얼굴 검출 및 정렬
    face_helper = FaceRestoreHelper(
        upscale_factor=1,
        face_size=512,
        crop_ratio=(1, 1),
        det_model='retinaface_resnet50',
        save_ext='png',
        use_parse=True,
        device=device
    )

    face_helper.read_image(input_image)
    face_helper.get_face_landmarks_5(only_center_face=False, resize=512, eye_dist_threshold=5)
    face_helper.align_warp_face()

    # 얼굴 복원
    for idx, cropped_face in enumerate(face_helper.cropped_faces):
        cropped_face_t = img2tensor(cropped_face / 255., bgr2rgb=True, float32=True).to(device)
        normalize(cropped_face_t, (0.5, 0.5, 0.5), (0.5, 0.5, 0.5), inplace=True)
        cropped_face_t = cropped_face_t.unsqueeze(0).to(device)

        try:
            with torch.no_grad():
                output = model(cropped_face_t, w=0.5, adain=True)[0]
                restored_face = tensor2img(output, rgb2bgr=True, min_max=(-1, 1))
            del output
            if use_gpu:
                torch.cuda.empty_cache()
        except RuntimeError as error:
            print(f'Error: {error}')
            print('If you encounter CUDA out of memory, try to set --tile with a smaller number.')
        else:
            restored_face = restored_face.astype('uint8')
            face_helper.add_restored_face(restored_face)

    # 결과 생성
    face_helper.get_inverse_affine(None)
    restored_img = face_helper.paste_faces_to_input_image()
    
    # 최종 이미지 크기 조정 (원본 크기로)
    restored_img = cv2.resize(restored_img, (w, h))

    return restored_img

if __name__ == "__main__":
    img = cv2.imread("cap3.jpg")
    restored_img = restore_face(img)
    cv2.imwrite('output.jpg', restored_img)