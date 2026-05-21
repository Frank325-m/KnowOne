"""
大语言模型工具模块
处理 LLM 的初始化、提示词构建和 RAG 问答链
"""

import logging
from typing import Optional, Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM

from config.settings import settings
from config.logging_config import get_logger
from .vector_utils import search_knowledge, search_with_rerank
from core.exceptions import (
    ModelError,
    ModelLoadError,
    ModelInferenceError,
    RetrievalError,
    NoRelevantDocumentsError,
    handle_rag_error
)

# 获取日志记录器
logger = get_logger(__name__)


@handle_rag_error
def get_local_llm(
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> OllamaLLM:
    """
    初始化本地大模型
    
    Args:
        model_name: 模型名称，如果为 None 则使用配置中的模型
        temperature: 温度参数，控制随机性
        max_tokens: 最大生成 token 数
        
    Returns:
        OllamaLLM 实例
        
    Raises:
        ModelLoadError: 如果无法加载模型
    """
    try:
        # 使用配置值或参数值
        if model_name is None:
            model_name = settings.LLM_MODEL_NAME
        if temperature is None:
            temperature = settings.LLM_TEMPERATURE
        if max_tokens is None:
            max_tokens = settings.LLM_MAX_TOKENS
        
        logger.info(f"正在加载本地大模型: {model_name}")
        logger.info(f"模型参数: temperature={temperature}, max_tokens={max_tokens}")
        
        llm = OllamaLLM(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=settings.REQUEST_TIMEOUT
        )
        
        # 测试模型连接
        try:
            test_response = llm.invoke("你好")
            logger.debug(f"模型连接测试成功，响应长度: {len(test_response)}")
        except Exception as test_error:
            logger.warning(f"模型连接测试失败: {test_error}")
            # 继续，可能在后续使用中会成功
        
        logger.info(f"本地大模型加载成功: {model_name}")
        return llm
        
    except Exception as e:
        logger.error(f"本地大模型加载失败: {e}")
        raise ModelLoadError(
            model_name=model_name or settings.LLM_MODEL_NAME,
            error=str(e)
        )


# RAG 专用提示词模板（核心防幻觉）
RAG_PROMPT_TEMPLATE = """
你是一个专业的问答助手，基于提供的上下文信息回答用户的问题。

约束规则：
1. 仅使用【上下文信息】内的内容作答，严谨编造外部知识
2. 如果上下文信息中没有相关答案，请直接回答："暂无相关知识库内容"
3. 回答要简洁通顺，条理清晰，不要多余废话
4. 如果问题与上下文信息无关，请说明："这个问题与当前知识库内容无关"
5. 保持回答的专业性和准确性

上下文信息：
{context}

问题：{question}

请基于以上上下文信息回答问题：
"""


@handle_rag_error
def build_rag_chain(
    use_rerank: bool = True,
    model_name: Optional[str] = None,
    prompt_template: Optional[str] = None
) -> Any:
    """
    构建 RAG 问答链
    
    Args:
        use_rerank: 是否使用重排检索
        model_name: 模型名称
        prompt_template: 提示词模板
        
    Returns:
        RAG 问答链
        
    Raises:
        ModelError: 如果无法构建问答链
    """
    try:
        # 使用配置值或参数值
        if prompt_template is None:
            prompt_template = RAG_PROMPT_TEMPLATE
        
        logger.info(f"正在构建 RAG 问答链，使用重排: {use_rerank}")
        
        # 创建提示词模板
        prompt = PromptTemplate.from_template(prompt_template)
        logger.debug(f"提示词模板已创建，长度: {len(prompt_template)} 字符")
        
        # 获取 LLM
        llm = get_local_llm(model_name=model_name)
        
        # 定义检索函数
        def retrieve_context(question: str) -> str:
            """检索上下文信息"""
            try:
                if not question or not question.strip():
                    logger.warning("检索问题为空")
                    return "无检索问题"
                
                logger.debug(f"开始检索上下文: '{question}'")
                
                if use_rerank:
                    context, docs = search_with_rerank(question)
                    logger.debug(f"重排检索完成，找到 {len(docs)} 个相关文档")
                else:
                    context, docs = search_knowledge(question)
                    logger.debug(f"普通检索完成，找到 {len(docs)} 个相关文档")
                
                # 限制上下文窗口大小
                context = limit_context_window(context, settings.MAX_CONTEXT_LENGTH)
                logger.debug(f"上下文处理完成，长度: {len(context)} 字符")
                
                return context
                
            except NoRelevantDocumentsError as e:
                logger.info(f"未找到相关文档: '{question}'")
                return "暂无相关知识库内容"
            except RetrievalError as e:
                logger.error(f"检索失败: {e}")
                return f"检索失败: {str(e)}"
            except Exception as e:
                logger.error(f"上下文检索异常: {e}")
                return f"上下文检索异常: {str(e)}"
        
        # 组装 RAG 链
        rag_chain = (
            {
                "context": lambda x: retrieve_context(x),
                "question": RunnablePassthrough()
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        
        logger.info("RAG 问答链构建成功")
        return rag_chain
        
    except Exception as e:
        logger.error(f"RAG 问答链构建失败: {e}")
        raise ModelError(
            message="无法构建 RAG 问答链",
            details={"error": str(e)}
        )


@handle_rag_error
def rag_chat(
    question: str,
    use_rerank: bool = True,
    model_name: Optional[str] = None
) -> str:
    """
    RAG 问答
    
    Args:
        question: 用户问题
        use_rerank: 是否使用重排检索
        model_name: 模型名称
        
    Returns:
        模型回答
        
    Raises:
        ModelInferenceError: 如果模型推理失败
    """
    try:
        if not question or not question.strip():
            logger.warning("问答问题为空")
            return "请输入有效的问题"
        
        logger.info(f"开始 RAG 问答: '{question}'")
        logger.info(f"使用重排: {use_rerank}, 模型: {model_name or settings.LLM_MODEL_NAME}")
        
        # 构建 RAG 链
        rag_chain = build_rag_chain(
            use_rerank=use_rerank,
            model_name=model_name
        )
        
        # 执行问答
        logger.debug(f"执行模型推理...")
        response = rag_chain.invoke(question)
        
        # 验证响应
        if not response or not response.strip():
            logger.warning("模型返回空响应")
            response = "模型未返回有效回答"
        
        logger.info(f"RAG 问答完成，响应长度: {len(response)} 字符")
        logger.debug(f"模型响应: {response[:200]}...")
        
        return response
        
    except ModelInferenceError as e:
        raise e
    except Exception as e:
        logger.error(f"RAG 问答失败: {e}")
        raise ModelInferenceError(
            model_name=model_name or settings.LLM_MODEL_NAME,
            input_data=question,
            error=str(e)
        )


@handle_rag_error
def limit_context_window(context: str, max_tokens: Optional[int] = None) -> str:
    """
    限制上下文窗口大小
    
    Args:
        context: 原始上下文
        max_tokens: 最大 token 数
        
    Returns:
        截断后的上下文
    """
    try:
        if max_tokens is None:
            max_tokens = settings.MAX_CONTEXT_LENGTH
        
        if not context:
            return ""
        
        original_length = len(context)
        
        if original_length <= max_tokens:
            return context
        
        # 截断上下文
        truncated_context = context[:max_tokens] + "\n...(内容过长已截断)"
        truncated_length = len(truncated_context)
        
        logger.debug(f"上下文截断: {original_length} -> {truncated_length} 字符")
        
        return truncated_context
        
    except Exception as e:
        logger.warning(f"上下文截断失败: {e}")
        return context


@handle_rag_error
def get_model_info(model_name: Optional[str] = None) -> Dict[str, Any]:
    """
    获取模型信息
    
    Args:
        model_name: 模型名称
        
    Returns:
        模型信息字典
    """
    try:
        if model_name is None:
            model_name = settings.LLM_MODEL_NAME
        
        info = {
            "model_name": model_name,
            "temperature": settings.LLM_TEMPERATURE,
            "max_tokens": settings.LLM_MAX_TOKENS,
            "embedding_model": settings.EMBED_MODEL_NAME,
            "context_length": settings.MAX_CONTEXT_LENGTH,
            "chunk_size": settings.CHUNK_SIZE,
            "chunk_overlap": settings.CHUNK_OVERLAP,
            "search_type": settings.SEARCH_TYPE,
            "default_top_k": settings.DEFAULT_TOP_K
        }
        
        logger.debug(f"模型信息: {info}")
        return info
        
    except Exception as e:
        logger.warning(f"获取模型信息失败: {e}")
        return {"error": str(e)}


@handle_rag_error
def test_model_connection(model_name: Optional[str] = None) -> Dict[str, Any]:
    """
    测试模型连接
    
    Args:
        model_name: 模型名称
        
    Returns:
        测试结果字典
    """
    try:
        if model_name is None:
            model_name = settings.LLM_MODEL_NAME
        
        logger.info(f"测试模型连接: {model_name}")
        
        # 获取模型
        llm = get_local_llm(model_name=model_name)
        
        # 测试查询
        test_question = "你好，请回复'模型连接正常'"
        logger.debug(f"发送测试查询: '{test_question}'")
        
        response = llm.invoke(test_question)
        
        result = {
            "success": True,
            "model_name": model_name,
            "response": response,
            "response_length": len(response),
            "message": "模型连接正常"
        }
        
        logger.info(f"模型连接测试成功: {model_name}")
        logger.debug(f"测试响应: {response}")
        
        return result
        
    except Exception as e:
        logger.error(f"模型连接测试失败: {e}")
        return {
            "success": False,
            "model_name": model_name or settings.LLM_MODEL_NAME,
            "error": str(e),
            "message": "模型连接失败"
        }


@handle_rag_error
def simple_chat(
    question: str,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None
) -> str:
    """
    简单聊天（不使用 RAG）
    
    Args:
        question: 用户问题
        model_name: 模型名称
        temperature: 温度参数
        
    Returns:
        模型回答
    """
    try:
        if not question or not question.strip():
            return "请输入有效的问题"
        
        logger.info(f"开始简单聊天: '{question}'")
        
        # 获取模型
        llm = get_local_llm(
            model_name=model_name,
            temperature=temperature
        )
        
        # 执行聊天
        response = llm.invoke(question)
        
        logger.info(f"简单聊天完成，响应长度: {len(response)} 字符")
        
        return response
        
    except Exception as e:
        logger.error(f"简单聊天失败: {e}")
        return f"聊天失败: {str(e)}"