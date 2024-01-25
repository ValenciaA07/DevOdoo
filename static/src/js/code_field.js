/** @odoo-module */
/** @odoo-module **/
const {xml, Component} = owl;
import { standardFieldProps } from "@web/views/fields/standard_field_props";
// Import the registry
import {registry} from "@web/core/registry";


export class CodeField extends Component {
    setup() {
        super.setup();
    }
}

CodeField.template = xml`<pre t-esc="props.value" decoration-info="bg-primary text-white p-3 rounded"/>`;
CodeField.props = standardFieldProps;

// Add the field to the correct category
registry.category("fields").add("code", CodeField);