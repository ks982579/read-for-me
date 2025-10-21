import torch
import subprocess
import re
from typing import Dict, Tuple


class GPUOptimizer:
    def __init__(self):
        self.gpu_info = self._detect_gpu()

    def _detect_gpu(self) -> Dict:
        """Detect GPU capabilities and return optimization settings"""
        gpu_info = {
            "has_gpu": False,
            "gpu_name": "CPU",
            "vram_gb": 0,
            "recommended_model": "microsoft/DialoGPT-small",
            "chunk_size": 1024,
            "batch_size": 1,
            "use_fp16": False
        }

        if not torch.cuda.is_available():
            return gpu_info

        try:
            # Get GPU info from nvidia-smi
            result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader,nounits'],
                                  capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if ',' in line:
                        name, memory = line.split(',', 1)
                        gpu_info["has_gpu"] = True
                        gpu_info["gpu_name"] = name.strip()
                        gpu_info["vram_gb"] = int(memory.strip()) // 1024  # Convert MB to GB
                        break

        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            # Fallback to torch detection
            if torch.cuda.is_available():
                gpu_info["has_gpu"] = True
                gpu_info["gpu_name"] = torch.cuda.get_device_name(0)
                # Estimate VRAM (torch doesn't give exact total)
                gpu_info["vram_gb"] = torch.cuda.get_device_properties(0).total_memory // (1024**3)

        # Optimize settings based on VRAM
        self._optimize_settings(gpu_info)
        return gpu_info

    def _optimize_settings(self, gpu_info: Dict) -> None:
        """Set optimal parameters based on GPU capabilities"""
        vram = gpu_info["vram_gb"]

        if vram >= 16:  # RTX 5070 Ti, 4080, 4090
            gpu_info.update({
                "recommended_model": "microsoft/Phi-3-mini-4k-instruct",  # High quality, efficient
                "fallback_models": ["google/flan-t5-large", "microsoft/DialoGPT-large"],
                "chunk_size": 3072,
                "batch_size": 4,
                "use_fp16": True,
                "max_new_tokens": 512,
                "performance_tier": "High-End"
            })
        elif vram >= 12:  # RTX 4070, 3080 Ti
            gpu_info.update({
                "recommended_model": "google/flan-t5-large",
                "fallback_models": ["google/flan-t5-base", "microsoft/DialoGPT-medium"],
                "chunk_size": 2048,
                "batch_size": 2,
                "use_fp16": True,
                "max_new_tokens": 400,
                "performance_tier": "High"
            })
        elif vram >= 8:   # RTX 4060 Ti, 3070
            gpu_info.update({
                "recommended_model": "google/flan-t5-base",
                "fallback_models": ["google/flan-t5-small", "microsoft/DialoGPT-medium"],
                "chunk_size": 1536,
                "batch_size": 2,
                "use_fp16": True,
                "max_new_tokens": 350,
                "performance_tier": "Medium-High"
            })
        elif vram >= 6:   # RTX 3060, 4060
            gpu_info.update({
                "recommended_model": "google/flan-t5-base",
                "fallback_models": ["google/flan-t5-small", "microsoft/DialoGPT-small"],
                "chunk_size": 1024,
                "batch_size": 1,
                "use_fp16": True,
                "max_new_tokens": 300,
                "performance_tier": "Medium"
            })
        else:  # Less than 6GB or CPU
            gpu_info.update({
                "recommended_model": "google/flan-t5-small",
                "fallback_models": ["microsoft/DialoGPT-small", "distilgpt2"],
                "chunk_size": 512,
                "batch_size": 1,
                "use_fp16": False,
                "max_new_tokens": 256,
                "performance_tier": "Basic"
            })

    def get_optimized_settings(self) -> Dict:
        """Return optimized settings for current GPU"""
        return self.gpu_info

    def print_gpu_analysis(self) -> None:
        """Print detailed GPU analysis and recommendations"""
        info = self.gpu_info

        print("🔍 GPU Analysis & Optimization")
        print("=" * 50)
        print(f"GPU: {info['gpu_name']}")
        print(f"VRAM: {info['vram_gb']}GB")
        print(f"Performance Tier: {info.get('performance_tier', 'Basic')}")
        print()

        print("📊 Optimized Settings:")
        print(f"• Recommended Model: {info['recommended_model']}")
        print(f"• Chunk Size: {info['chunk_size']} tokens")
        print(f"• Batch Size: {info['batch_size']}")
        print(f"• FP16 Precision: {info['use_fp16']}")
        print(f"• Max New Tokens: {info['max_new_tokens']}")
        print()

        # Performance estimates
        estimated_speed = self._estimate_processing_speed(info['vram_gb'])
        print("⚡ Performance Estimates:")
        print(f"• Processing Speed: ~{estimated_speed} seconds per chunk")
        print(f"• 685-page book: ~{self._estimate_book_time(estimated_speed)} minutes")
        print()

        if info['vram_gb'] >= 16:
            print("🚀 Your GPU can handle:")
            print("• Large language models (7B+ parameters)")
            print("• Multiple models simultaneously")
            print("• Real-time processing for most documents")
            print("• Advanced models like CodeLlama for code analysis")
        elif info['vram_gb'] >= 12:
            print("✅ Your GPU is excellent for:")
            print("• High-quality text summarization")
            print("• Fast processing of technical documents")
            print("• Most state-of-the-art models")
        elif info['vram_gb'] >= 6:
            print("👍 Your GPU works well for:")
            print("• Good quality document processing")
            print("• Reasonable processing speeds")
            print("• Most common AI tasks")

    def _estimate_processing_speed(self, vram_gb: int) -> float:
        """Estimate processing speed based on VRAM"""
        if vram_gb >= 16:
            return 1.5  # Very fast
        elif vram_gb >= 12:
            return 2.5  # Fast
        elif vram_gb >= 8:
            return 4.0  # Good
        elif vram_gb >= 6:
            return 6.0  # Moderate
        else:
            return 10.0  # Slow

    def _estimate_book_time(self, speed_per_chunk: float) -> int:
        """Estimate time to process 685-page book"""
        # Rough estimate: ~1.5 chunks per page on average
        estimated_chunks = 685 * 1.5
        total_seconds = estimated_chunks * speed_per_chunk
        return int(total_seconds / 60)


def main():
    optimizer = GPUOptimizer()
    optimizer.print_gpu_analysis()

    print("\n🎯 Recommended Command:")
    settings = optimizer.get_optimized_settings()
    cmd = f"python main.py your_book.pdf --model \"{settings['recommended_model']}\" --chunk-size {settings['chunk_size']}"
    print(cmd)


if __name__ == "__main__":
    main()