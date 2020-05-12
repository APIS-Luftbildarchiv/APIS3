<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.8.3-Zanzibar" simplifyLocal="1" minScale="1e+08" simplifyAlgorithm="0" styleCategories="AllStyleCategories" simplifyMaxScale="1" maxScale="0" readOnly="0" hasScaleBasedVisibilityFlag="0" simplifyDrawingTol="1" labelsEnabled="0" simplifyDrawingHints="1">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 type="singleSymbol" enableorderby="0" forceraster="0" symbollevels="0">
    <symbols>
      <symbol type="line" clip_to_extent="1" alpha="1" name="0" force_rhr="0">
        <layer pass="0" class="SimpleLine" locked="0" enabled="1">
          <prop v="round" k="capstyle"/>
          <prop v="5;2" k="customdash"/>
          <prop v="3x:0,0,0,0,0,0" k="customdash_map_unit_scale"/>
          <prop v="MM" k="customdash_unit"/>
          <prop v="0" k="draw_inside_polygon"/>
          <prop v="round" k="joinstyle"/>
          <prop v="27,153,111,255" k="line_color"/>
          <prop v="solid" k="line_style"/>
          <prop v="0.6" k="line_width"/>
          <prop v="MM" k="line_width_unit"/>
          <prop v="0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0" k="ring_filter"/>
          <prop v="0" k="use_custom_dash"/>
          <prop v="3x:0,0,0,0,0,0" k="width_map_unit_scale"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <customproperties>
    <property value="0" key="embeddedWidgets/count"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
    <DiagramCategory opacity="1" width="15" scaleDependency="Area" barWidth="5" sizeScale="3x:0,0,0,0,0,0" lineSizeType="MM" backgroundColor="#ffffff" enabled="0" diagramOrientation="Up" lineSizeScale="3x:0,0,0,0,0,0" height="15" minimumSize="0" sizeType="MM" scaleBasedVisibility="0" maxScaleDenominator="1e+08" penWidth="0" penAlpha="255" rotationOffset="270" labelPlacementMethod="XHeight" minScaleDenominator="0" penColor="#000000" backgroundAlpha="255">
      <fontProperties description="MS Shell Dlg 2,7.875,-1,5,50,0,0,0,0,0" style=""/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings placement="2" showAll="1" priority="0" dist="0" zIndex="0" obstacle="0" linePlacementFlags="18">
    <properties>
      <Option type="Map">
        <Option type="QString" value="" name="name"/>
        <Option name="properties"/>
        <Option type="QString" value="collection" name="type"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <fieldConfiguration>
    <field name="filmnummer">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="flugweg_quelle">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="flugdatum">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="fotograf">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="pilot">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="flugzeug">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="abflug_zeit">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="ankunft_zeit">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="flugzeit">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="abflug_flughafen">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="ankunft_flughafen">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="wetter">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="target">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" name="" field="filmnummer"/>
    <alias index="1" name="" field="flugweg_quelle"/>
    <alias index="2" name="" field="flugdatum"/>
    <alias index="3" name="" field="fotograf"/>
    <alias index="4" name="" field="pilot"/>
    <alias index="5" name="" field="flugzeug"/>
    <alias index="6" name="" field="abflug_zeit"/>
    <alias index="7" name="" field="ankunft_zeit"/>
    <alias index="8" name="" field="flugzeit"/>
    <alias index="9" name="" field="abflug_flughafen"/>
    <alias index="10" name="" field="ankunft_flughafen"/>
    <alias index="11" name="" field="wetter"/>
    <alias index="12" name="" field="target"/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default expression="" applyOnUpdate="0" field="filmnummer"/>
    <default expression="" applyOnUpdate="0" field="flugweg_quelle"/>
    <default expression="" applyOnUpdate="0" field="flugdatum"/>
    <default expression="" applyOnUpdate="0" field="fotograf"/>
    <default expression="" applyOnUpdate="0" field="pilot"/>
    <default expression="" applyOnUpdate="0" field="flugzeug"/>
    <default expression="" applyOnUpdate="0" field="abflug_zeit"/>
    <default expression="" applyOnUpdate="0" field="ankunft_zeit"/>
    <default expression="" applyOnUpdate="0" field="flugzeit"/>
    <default expression="" applyOnUpdate="0" field="abflug_flughafen"/>
    <default expression="" applyOnUpdate="0" field="ankunft_flughafen"/>
    <default expression="" applyOnUpdate="0" field="wetter"/>
    <default expression="" applyOnUpdate="0" field="target"/>
  </defaults>
  <constraints>
    <constraint constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0" field="filmnummer"/>
    <constraint constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0" field="flugweg_quelle"/>
    <constraint constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0" field="flugdatum"/>
    <constraint constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0" field="fotograf"/>
    <constraint constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0" field="pilot"/>
    <constraint constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0" field="flugzeug"/>
    <constraint constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0" field="abflug_zeit"/>
    <constraint constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0" field="ankunft_zeit"/>
    <constraint constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0" field="flugzeit"/>
    <constraint constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0" field="abflug_flughafen"/>
    <constraint constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0" field="ankunft_flughafen"/>
    <constraint constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0" field="wetter"/>
    <constraint constraints="0" unique_strength="0" notnull_strength="0" exp_strength="0" field="target"/>
  </constraints>
  <constraintExpressions>
    <constraint desc="" exp="" field="filmnummer"/>
    <constraint desc="" exp="" field="flugweg_quelle"/>
    <constraint desc="" exp="" field="flugdatum"/>
    <constraint desc="" exp="" field="fotograf"/>
    <constraint desc="" exp="" field="pilot"/>
    <constraint desc="" exp="" field="flugzeug"/>
    <constraint desc="" exp="" field="abflug_zeit"/>
    <constraint desc="" exp="" field="ankunft_zeit"/>
    <constraint desc="" exp="" field="flugzeit"/>
    <constraint desc="" exp="" field="abflug_flughafen"/>
    <constraint desc="" exp="" field="ankunft_flughafen"/>
    <constraint desc="" exp="" field="wetter"/>
    <constraint desc="" exp="" field="target"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig actionWidgetStyle="dropDown" sortOrder="0" sortExpression="">
    <columns>
      <column type="field" width="-1" hidden="0" name="filmnummer"/>
      <column type="field" width="-1" hidden="0" name="flugweg_quelle"/>
      <column type="field" width="-1" hidden="0" name="flugdatum"/>
      <column type="field" width="-1" hidden="0" name="fotograf"/>
      <column type="field" width="-1" hidden="0" name="pilot"/>
      <column type="field" width="-1" hidden="0" name="flugzeug"/>
      <column type="field" width="-1" hidden="0" name="abflug_zeit"/>
      <column type="field" width="-1" hidden="0" name="ankunft_zeit"/>
      <column type="field" width="-1" hidden="0" name="flugzeit"/>
      <column type="field" width="-1" hidden="0" name="abflug_flughafen"/>
      <column type="field" width="-1" hidden="0" name="ankunft_flughafen"/>
      <column type="field" width="-1" hidden="0" name="wetter"/>
      <column type="field" width="-1" hidden="0" name="target"/>
      <column type="actions" width="-1" hidden="1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <editform tolerant="1"></editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field editable="1" name="abflug_flughafen"/>
    <field editable="1" name="abflug_zeit"/>
    <field editable="1" name="ankunft_flughafen"/>
    <field editable="1" name="ankunft_zeit"/>
    <field editable="1" name="filmnummer"/>
    <field editable="1" name="flugdatum"/>
    <field editable="1" name="flugweg_quelle"/>
    <field editable="1" name="flugzeit"/>
    <field editable="1" name="flugzeug"/>
    <field editable="1" name="fotograf"/>
    <field editable="1" name="pilot"/>
    <field editable="1" name="target"/>
    <field editable="1" name="wetter"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="abflug_flughafen"/>
    <field labelOnTop="0" name="abflug_zeit"/>
    <field labelOnTop="0" name="ankunft_flughafen"/>
    <field labelOnTop="0" name="ankunft_zeit"/>
    <field labelOnTop="0" name="filmnummer"/>
    <field labelOnTop="0" name="flugdatum"/>
    <field labelOnTop="0" name="flugweg_quelle"/>
    <field labelOnTop="0" name="flugzeit"/>
    <field labelOnTop="0" name="flugzeug"/>
    <field labelOnTop="0" name="fotograf"/>
    <field labelOnTop="0" name="pilot"/>
    <field labelOnTop="0" name="target"/>
    <field labelOnTop="0" name="wetter"/>
  </labelOnTop>
  <widgets/>
  <previewExpression>filmnummer</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>1</layerGeometryType>
</qgis>
