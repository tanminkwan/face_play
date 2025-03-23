from app import storage, face_detector, face_swapper, face_restorer

def update_images_by_face(bucket_name, file_name, image, face, target_face=None, face_seq=0, restore=False):
    
    if not target_face:
        faces = face_detector.get(image)
        target_face = faces[face_seq]

    img_face = face_swapper.get(image, target_face, face)

    if restore:
        img_face = face_restorer.restore(img_face)

    storage.upload_image(bucket_name, file_name, image=img_face)