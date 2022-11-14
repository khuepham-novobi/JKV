from odoo import api, models
import base64
import cv2
import logging
_logger = logging.getLogger(__name__)


# Resize a image and maintains aspect ratio
def maintain_aspect_ratio_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    # Grab the image size and initialize dimensions
    dim = None
    (h, w) = image.shape[:2]

    # Return original image if no need to resize
    if width is None and height is None:
        return image

    # We are resizing height if width is none
    if width is None:
        # Calculate the ratio of the height and construct the dimensions
        r = height / float(h)
        dim = (int(w * r), height)
    # We are resizing width if height is none
    else:
        # Calculate the ratio of the width and construct the dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # Return the resized image
    return cv2.resize(image, dim, interpolation=inter)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def init_video_frame(self):
        count = 0
        product_templates = self.env['product.template'].search([])
        for record in product_templates:
            if not record.image:
                try:
                    cap = cv2.VideoCapture(record.sample_file_url or record.livestream_video_sample_file_url)
                    # cap = cv2.VideoCapture("https://jkv-videos.s3.amazonaws.com/68-345-123-1-sample.mp4")
                    success, frame = cap.read()
                    if cap.isOpened() and success:
                        resize_frame = maintain_aspect_ratio_resize(frame, width=400)
                        success, buffer_image = cv2.imencode('.jpg', resize_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                        if success:
                            record.sudo().write({'image': base64.b64encode(buffer_image)})
                            self._cr.commit()
                            count += 1
                            _logger.info("Video capture count: %s", count)

                    cap.release()
                    cv2.destroyAllWindows()

                except Exception, e:
                    _logger.info("Error create video frame : %s", e)


class JKVFileName(models.Model):
    _inherit = "jkv.filename"

    @api.model
    def create(self, values):
        new_id = super(JKVFileName, self).create(values)
        product_template = self.env['product.template'].search([('filename_id', '=', new_id.id)])

        # Create video frame
        try:
            cap = cv2.VideoCapture(product_template.sample_file_url)
            # cap = cv2.VideoCapture("https://jkv-videos.s3.amazonaws.com/76-532-251-1-sample.mp4")
            success, frame = cap.read()
            if cap.isOpened() and success:
                resize_frame = maintain_aspect_ratio_resize(frame, width=400)
                success, buffer_image = cv2.imencode('.jpg', resize_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if success:
                    product_template.image = base64.b64encode(buffer_image)
                    _logger.info("Video capture product.template id : %s", product_template.id)
            else:
                product_template.image = None
            cap.release()
            cv2.destroyAllWindows()
        except Exception, e:
            _logger.info("Error create video frame : %s", e)

        return new_id

    @api.multi
    def write(self, values):
        status = super(JKVFileName, self).write(values)
        for record in self:
            product_template = self.env['product.template'].search([('filename_id', '=', record.id)])

            # Create video frame
            try:
                cap = cv2.VideoCapture(product_template.sample_file_url)
                # cap = cv2.VideoCapture("https://jkv-videos.s3.amazonaws.com/76-532-251-1-sample.mp4")
                success, frame = cap.read()
                if cap.isOpened() and success:
                    resize_frame = maintain_aspect_ratio_resize(frame, width=400)
                    success, buffer_image = cv2.imencode('.jpg', resize_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    if success:
                        product_template.image = base64.b64encode(buffer_image)
                        _logger.info("Video capture product.template id : %s", product_template.id)
                else:
                    product_template.image = None
                cap.release()
                cv2.destroyAllWindows()
            except Exception, e:
                _logger.info("Error update video frame : %s", e)

        return status





