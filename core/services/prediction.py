# coding: utf-8

from typing import Optional

import cv2
import numpy as np
from dataclasses import dataclass
from keras import Sequential
from keras import backend as k_backend
from keras.applications.vgg16 import preprocess_input
from keras.preprocessing import image as k_image

from core.config import CalculationConfig
from core.models.image import Image
from core.models.prediction import Prediction
from core.utils.nn_model import get_model, get_config


@dataclass(frozen=True)
class PredictionService:
    model: Sequential
    config: CalculationConfig

    def _image_tensor(self, image: Image) -> np.ndarray:
        img_path = image.path.as_posix()
        img = k_image.load_img(
            img_path, target_size=(self.config.width, self.config.height)
        )
        img_tensor = k_image.image.img_to_array(img)
        img_tensor = np.expand_dims(img_tensor, axis=0)
        img_tensor /= 255
        return img_tensor

    def predict(self, image: Image) -> Prediction:
        tensor = self._image_tensor(image)
        prediction = self.model.predict(tensor)[0]
        normal, pneumonia = prediction
        return Prediction(normal=normal, pneumonia=pneumonia)

    def attention(self, image: Image) -> Image:
        img_path = image.path.as_posix()

        width, height = self.config.width, self.config.height
        img = k_image.load_img(img_path, target_size=(width, height))
        x = k_image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)

        vgg16 = self.model.get_layer("vgg16")
        last_conv_layer = vgg16.get_layer("block5_conv3")

        o = vgg16.get_output_at(0)[:, 8]
        grads = k_backend.gradients(o, last_conv_layer.output)[0]
        pooled_grads = k_backend.mean(grads, axis=(0, 1, 2))
        iterate = k_backend.function(
            [vgg16.get_input_at(0)], [pooled_grads, last_conv_layer.output[0]]
        )
        pooled_grads_value, conv_layer_output_value = iterate([x])
        for i in range(512):
            conv_layer_output_value[:, :, i] *= pooled_grads_value[i]
        heatmap = np.mean(conv_layer_output_value, axis=-1)
        heatmap = np.maximum(heatmap, 0)
        heatmap /= np.max(heatmap)

        cv2_image = cv2.imread(img_path)
        heatmap = cv2.resize(heatmap, (cv2_image.shape[1], cv2_image.shape[0]))
        heatmap = np.uint8(255 * heatmap)
        heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        superimposed_img = heatmap * 0.4 + cv2_image

        # cv2.imwrite("pneumo.jpg", superimposed_img)

        cache_dir = image.path.parent.joinpath("cache")
        cache_dir.mkdir(parents=True, exist_ok=True)

        new_image_path = cache_dir.joinpath(image.path.name)
        cv2.imwrite(new_image_path.as_posix(), superimposed_img)

        return Image(new_image_path)


@dataclass(frozen=True)
class PredictionServiceFactory:
    instance: Optional[PredictionService] = None

    @classmethod
    def create(cls) -> PredictionService:
        if cls.instance is not None:
            return cls.instance

        model = get_model()
        config = get_config()

        cls.instance = PredictionService(model, config)
        return cls.instance


# if __name__ == "__main__":
#     test_image = Image(
#         # Path(r"D:\ml\input\chest_xray\test\NORMAL\IM-0001-0001.jpeg")
#         Path(r"D:\ml\input\chest_xray\test\PNEUMONIA\person1_virus_7.jpeg")
#     )
#     service = PredictionServiceFactory.create()
#     attention = service.attention(test_image)
