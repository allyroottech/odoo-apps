import { Component } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { _t } from "@web/core/l10n/translation";

export class AttachmentPreviewDialog extends Component {
    static template = "chatter_attachment_preview.AttachmentPreviewDialog";
    static components = { Dialog };
    static props = {
        attachment: Object,
        close: Function,
    };

    get previewUrl() {
        const params = new URLSearchParams();
        const token = this.props.attachment.raw_access_token || this.props.attachment.access_token;
        if (token) {
            params.set("access_token", token);
        }
        const query = params.toString();
        return `/chatter_attachment_preview/preview/${this.props.attachment.id}${query ? `?${query}` : ""}`;
    }

    get title() {
        return this.props.attachment.name || _t("Attachment Preview");
    }

    get downloadUrl() {
        return this.props.attachment.downloadUrl;
    }
}
