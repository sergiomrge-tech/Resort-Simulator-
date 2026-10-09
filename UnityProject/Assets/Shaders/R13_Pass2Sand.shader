Shader "Resort/R13/Pass2Sand" {
 Properties {
  _BaseMap("Dry sand",2D)="white" {} _WetMap("Wet sand",2D)="white" {}
  _BumpMap("Fine normal",2D)="bump" {}
 }
 SubShader {
  Tags {"RenderPipeline"="UniversalPipeline" "RenderType"="Opaque" "Queue"="Geometry"}
  Pass {
   Tags {"LightMode"="UniversalForward"} Cull Back ZWrite On
   HLSLPROGRAM
   #pragma vertex vert
   #pragma fragment frag
   #pragma multi_compile_fog
   #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
   #pragma multi_compile_fragment _ _SHADOWS_SOFT
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
   TEXTURE2D(_BaseMap);SAMPLER(sampler_BaseMap);
   TEXTURE2D(_WetMap);SAMPLER(sampler_WetMap);
   TEXTURE2D(_BumpMap);SAMPLER(sampler_BumpMap);
   CBUFFER_START(UnityPerMaterial)
    float4 _BaseMap_ST;
   CBUFFER_END
   struct A {float4 positionOS:POSITION;float2 uv:TEXCOORD0;};
   struct V {float4 positionCS:SV_POSITION;float3 world:TEXCOORD0;float2 uv:TEXCOORD1;float fog:TEXCOORD2;};
   V vert(A a){V o;VertexPositionInputs p=GetVertexPositionInputs(a.positionOS.xyz);o.positionCS=p.positionCS;o.world=p.positionWS;o.uv=a.uv;o.fog=ComputeFogFactor(p.positionCS.z);return o;}
   half4 frag(V v):SV_Target {
    // UV0 is global longitudinal / shoreline metres divided by four.
    float d=v.uv.y*4;float dry=smoothstep(2.5,10.0,d);
    half3 albedo=lerp(SAMPLE_TEXTURE2D(_WetMap,sampler_WetMap,v.uv).rgb,SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,v.uv).rgb,dry);
    float wear=1-.045*exp(-pow((d-23)/1.8,2));albedo*=wear;
    half3 map=UnpackNormal(SAMPLE_TEXTURE2D(_BumpMap,sampler_BumpMap,v.uv));
    half3 n=normalize(half3(0,1,0)+half3(.694658,0,-.719340)*map.x*.30+half3(-.719340,0,-.694658)*map.y*.30);
    Light sun=GetMainLight(TransformWorldToShadowCoord(v.world));
    half3 diffuse=albedo*(max(SampleSH(n),0)+sun.color*saturate(dot(n,sun.direction))*sun.shadowAttenuation);
    return half4(MixFog(diffuse,v.fog),1);
   }
   ENDHLSL
  }
 }
}
