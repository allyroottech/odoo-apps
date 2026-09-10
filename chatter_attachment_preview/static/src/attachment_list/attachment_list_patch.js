import { AttachmentList } from "@mail/core/common/attachment_list";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

import { AttachmentPreviewDialog } from "../attachment_preview/attachment_preview_dialog";

patch(AttachmentList.prototype, {
    getActions(attachment) {
        const res = super.getActions(...arguments);
        if (this.canPreviewAttachment(attachment)) {
            res.unshift({
                label: _t("Preview"),
                icon: "fa fa-eye",
                onSelect: () => this.onClickPreviewAttachment(attachment),
            });
        }
        return res;
    },

    canPreviewAttachment(attachment) {
        return !attachment.uploading && attachment.type !== "url";
    },

    onClickPreviewAttachment(attachment) {
        this.dialog.add(AttachmentPreviewDialog, { attachment });
    },
});
